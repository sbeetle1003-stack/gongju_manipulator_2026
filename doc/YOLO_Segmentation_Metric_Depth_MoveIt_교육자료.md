# YOLO Segmentation + Metric Depth 기반 MoveIt Planning Scene Monitor 교육자료

## 1. 교육 목표

이 교육자료는 단안 카메라 한 대를 이용하여 물체를 Instance Segmentation하고, Metric Depth 모델로 물체의 3차원 위치와 크기를 추정한 뒤 MoveIt Planning Scene Monitor에 실시간 반영하는 과정을 다룬다.

비교 구성:

1. **YOLO Segmentation + Depth Anything V2 Metric**
2. **YOLO Segmentation + MoGe-2 ViT-S**

이번 개정에서는 다음 문제를 추가로 다룬다.

- 기본 YOLO 모델이 실제로 검출할 수 있는 물체
- OpenMANIPULATOR-X가 집을 수 있는 COCO Class 후보
- 빨간 공·무지 박스·ArUco 박스에 기본 YOLO가 적합하지 않은 이유
- Gazebo에서 실습 물체 모델을 준비하는 방법
- 기본 사전학습 모델, Open-Vocabulary 모델, Custom 학습 모델의 선택 기준

---

## 2. 전체 시스템 구조

```text
/camera/image_raw
/camera/camera_info
/tf
        ↓
YOLO Instance Segmentation
        ├─ class_id
        ├─ confidence
        ├─ bounding_box
        └─ instance_mask
        ↓
Metric Geometry
        ├─ Depth Anything V2 Metric
        └─ MoGe-2 Metric Point Map
        ↓
Mask 내부 3D Point 추출
        ↓
Outlier Removal + 3D Bounding Box
        ↓
TF2: camera_optical_frame → base_link
        ↓
CollisionObject 또는 PointCloud2
        ↓
PlanningSceneMonitor
```

---

# Part 1. YOLO 모델과 실습 물체 선정

## 3. 기본 YOLO Segmentation 모델의 클래스 범위

Ultralytics의 일반적인 `-seg` 사전학습 모델은 COCO Instance Segmentation의 80개 클래스를 사용한다. 따라서 영상에 물체가 보인다고 해서 모든 물체를 검출하는 것은 아니다.

OpenMANIPULATOR-X 실습과 관계가 있는 대표 COCO 클래스는 다음과 같다.

| COCO Class | 실습 물체 예 | 집기 적합성 | Gazebo 준비 난이도 | 권장도 |
| --- | --- | ---: | ---: | ---: |
| sports ball | 테니스공 크기 공, 소형 장난감 공 | 높음 | 매우 낮음 | 높음 |
| bottle | 소형 플라스틱 병 | 높음 | 낮음 | 매우 높음 |
| cup | 플라스틱 컵, 작은 머그 | 높음 | 낮음 | 매우 높음 |
| bowl | 소형 플라스틱 그릇 | 중간 | 낮음 | 높음 |
| banana | 플라스틱 바나나 | 중간 | 낮음 | 높음 |
| apple | 플라스틱 사과 | 높음 | 낮음 | 매우 높음 |
| orange | 플라스틱 오렌지 | 높음 | 낮음 | 매우 높음 |
| carrot | 플라스틱 당근 | 중간 | 낮음 | 높음 |
| book | 얇은 소형 책 또는 노트 | 낮음 | 매우 낮음 | 보통 |
| cell phone | 모형 스마트폰 | 낮음 | 매우 낮음 | 보통 |
| remote | 리모컨 모형 | 중간 | 매우 낮음 | 높음 |
| scissors | 안전 가위·플라스틱 가위 | 중간 | 낮음 | 보통 |
| teddy bear | 작은 봉제·플라스틱 인형 | 낮음 | 낮음 | 보통 |
| toothbrush | 큰 모형 칫솔 | 중간 | 낮음 | 보통 |
| fork/spoon | 플라스틱 식기 | 낮음 | 낮음 | 낮음 |

OpenMANIPULATOR-X의 그리퍼 폭, 물체 무게, 마찰계수와 접근 방향을 고려하면 다음 물체가 가장 안정적이다.

```text
1순위: bottle, cup, apple, orange
2순위: sports ball, bowl, remote, carrot
3순위: banana, scissors, toothbrush, book
```

## 4. 빨간 공은 왜 애매한가

COCO에는 `sports ball` 클래스가 있지만 모든 빨간색 구체가 스포츠공으로 학습된 것은 아니다.

다음 경우에는 검출률이 낮을 수 있다.

- 단색이고 무늬가 전혀 없는 공
- 영상에서 공의 지름이 매우 작음
- COCO 학습 영상의 스포츠공과 외형이 다름
- Gazebo에서 재질이 지나치게 균일함
- 조명이 단순하여 실제 영상의 Texture와 차이가 큼

따라서 빨간 공은 다음 방식이 더 적합하다.

```text
빨간 공 위치 검출:
HSV + Contour + Hough Circle

공의 정밀 Mask:
HSV Mask 또는 SAM Prompt

AI 검출 비교 실습:
YOLO COCO sports ball 결과와 HSV 결과 비교
```

수업에서 기본 YOLO를 반드시 사용하려면 공에 축구공·테니스공과 유사한 Texture를 적용하는 편이 좋다.

## 5. 무지 사각 박스와 ArUco 박스

COCO 기본 클래스에는 일반적인 `box`, `cube`, `cardboard box`, `aruco box`가 없다. 따라서 단순 사각 박스를 기본 YOLO-Seg 모델로 안정적으로 검출하기 어렵다.

ArUco가 붙은 박스는 다음처럼 처리해야 한다.

```text
ArUco Marker 검출
        ↓
solvePnP
        ↓
박스 Pose 계산
        ↓
알려진 실제 박스 크기 적용
        ↓
CollisionObject 생성
```

ArUco 방식은 물체의 실제 크기와 6D Pose를 직접 계산할 수 있으므로 Metric Depth 모델보다 정확한 기준 실험으로 활용할 수 있다.

권장 비교 실습:

```text
방법 A: ArUco + solvePnP
방법 B: YOLO Custom Segmentation + Metric Depth
방법 C: SAM Prompt + Metric Depth
```

## 6. 기본 YOLO에 적합한 교육용 실물 물체

실제 교실에서 확보하기 쉬운 물체:

- 200~350 mL 불투명 플라스틱 병
- 작은 플라스틱 컵
- 장난감 사과·오렌지·바나나
- 테니스공 또는 무늬가 있는 소형 공
- 소형 플라스틱 그릇
- 리모컨 모형
- 작은 봉제 인형

주의사항:

- 투명 컵·투명 병은 Segmentation과 단안 Depth 모두 어려움
- 유광 금속은 반사 때문에 Depth 오차가 큼
- 검정 물체는 조명에 따라 경계가 사라질 수 있음
- 너무 작은 물체는 YOLO 입력 Resize 후 Mask가 무너질 수 있음
- 무거운 실제 캔·유리컵 대신 가벼운 모형을 사용

권장 크기:

```text
가로·세로: 4~10 cm
높이      : 5~15 cm
무게      : 가능한 한 100 g 이하
```

---

# Part 2. Gazebo 실습 물체 확보

## 7. Gazebo Fuel 사용

Gazebo Fuel에는 다양한 공개 모델이 있으며 Gazebo GUI 또는 URI로 World에 삽입할 수 있다.

검색 키워드 예:

```text
bottle
cup
mug
bowl
apple
orange
banana
ball
can
household object
YCB
```

Fuel 모델을 바로 사용할 때 확인할 항목:

- License
- Visual Mesh와 Collision Mesh 존재 여부
- 모델 크기 단위
- 질량과 Inertia
- Collision 형상의 복잡도
- Texture 경로
- Gazebo Harmonic 호환 여부
- 다운로드 용량

Fuel 자산은 제작자마다 품질과 Scale이 다를 수 있으므로 수업 전에 강사가 검증한 모델만 제공한다.

## 8. YCB Object Set 활용

YCB Object Set은 로봇 조작 연구를 위해 만들어진 표준 물체 집합이다. 음식, 주방용품, 공구, 형상 물체 등이 포함되며 RGB-D Scan, Mesh와 물리 정보가 제공된다.

YOLO COCO 클래스와 비교적 잘 연결되는 YCB 후보:

| YCB 계열 물체 | 가까운 COCO Class | 수업 활용 |
| --- | --- | --- |
| plastic apple | apple | 집기·분류 |
| plastic orange | orange | 집기·분류 |
| plastic banana | banana | 자세 변화 실험 |
| mug | cup | 손잡이 포함 Mask 실험 |
| bowl | bowl | 내부가 빈 물체 Depth 실험 |
| scissors | scissors | 복잡한 형상 Mask 실험 |
| bottle-like container | bottle | 세로 물체 집기 |
| foam brick / wood block | 해당 없음 | Custom 모델 또는 ArUco |
| cracker/sugar/pudding box | 해당 없음 | Custom box 학습 |
| tomato soup can | 직접 대응 없음 | Custom can 학습 권장 |

YCB 메시를 Gazebo에서 사용하려면 SDF Model Wrapper가 필요할 수 있다.

```text
model.sdf
model.config
meshes/visual.dae 또는 obj
meshes/collision.stl
materials/textures/
```

## 9. 가장 안정적인 Gazebo 자산 전략

### 전략 A. Primitive + Texture

```text
Bottle: cylinder + bottle texture
Cup   : cylinder + handle 생략 또는 mesh
Apple : sphere + apple texture
Orange: sphere + orange texture
Ball  : sphere + sports ball texture
```

장점:

- Collision이 안정적
- Scale과 질량 조절이 쉬움
- 수업용 PC에서 가벼움

단점:

- 실제 영상과 Domain Gap이 큼
- 단순 재질이면 YOLO가 인식하지 못할 수 있음

### 전략 B. YCB Mesh 사용

장점:

- 조작 연구에 적합한 실제 물체 형상
- 실제 물체와 시뮬레이션을 연결하기 쉬움

단점:

- Mesh 최적화 필요
- Collision Mesh가 복잡하면 시뮬레이션이 느려짐

### 전략 C. 직접 제작한 Custom Box

- SDF Box Primitive 사용
- 각 면에 다양한 Texture 또는 ArUco 부착
- Gazebo 카메라로 자동 데이터 생성
- Custom YOLO-Seg 학습

이 방식은 교육적으로 가장 가치가 높다.

---

# Part 3. 추천 YOLO 모델

## 10. 기본 COCO Segmentation 모델

2026년 Ultralytics 문서 기준으로 최신 COCO 사전학습 Segment 계열은 `YOLO26*-seg`이다. 환경 재현성과 기존 예제 호환성을 고려하면 수업에서는 설치된 Ultralytics 버전에서 공식 지원하는 모델을 선택해야 한다.

권장 예:

```python
from ultralytics import YOLO

model = YOLO("yolo26n-seg.pt")
results = model.predict(frame, conf=0.45, imgsz=640)
```

환경이 이전 Ultralytics 버전이라면 다음과 같은 기존 Segment 모델을 사용할 수 있다.

```text
yolov8n-seg.pt
yolov8s-seg.pt
yolo11n-seg.pt
yolo11s-seg.pt
```

선택 기준:

| 환경 | 권장 모델 규모 |
| --- | --- |
| CPU 전용 | nano, 입력 320~512 |
| 일반 노트북 GPU | nano 또는 small, 입력 640 |
| 데스크톱 NVIDIA GPU | small 또는 medium |
| ROS + Depth + Dashboard 동시 실행 | nano 우선 |

교육용 기본 권장:

```text
1차: 공식 nano segmentation 모델
2차: 정확도 부족 시 small segmentation 모델
```

## 11. 추천 대상 Class

기본 COCO 모델을 그대로 활용하는 실습은 다음 조합을 권장한다.

### 실습 세트 A

```text
bottle + cup + apple + orange
```

장점:

- 실물 확보가 쉬움
- YCB 또는 Gazebo 메시 확보가 비교적 쉬움
- 물체 크기가 그리퍼 실습에 적절함
- Class가 명확히 다름

### 실습 세트 B

```text
sports ball + bottle + bowl
```

장점:

- 구·원통·그릇의 3차원 형상 차이 비교
- Metric Depth Box 크기 추정 비교

### 실습 세트 C

```text
banana + apple + orange + carrot
```

장점:

- 형태가 다른 식품 클래스 분류
- 과일 자동 분류 프로젝트에 적합

## 12. YOLO-World 사용

일반 YOLO의 고정 COCO 클래스에 없는 물체를 재학습 없이 시험하려면 YOLO-World를 사용할 수 있다.

```python
from ultralytics import YOLOWorld

model = YOLOWorld("yolov8s-worldv2.pt")
model.set_classes([
    "red ball",
    "cardboard box",
    "wooden block",
    "aruco marker box",
])

results = model.predict(frame, conf=0.25)
```

장점:

- Text Prompt로 임의 Class를 지정
- Custom 학습 전에 가능성 확인
- 일반 박스·블록 탐색에 활용 가능

한계:

- 공식 Ultralytics YOLO-World는 주로 Detection Box 출력
- 정밀 Instance Mask가 필요한 현재 파이프라인에는 추가 Segmentation 단계 필요
- 작은 물체와 Gazebo 합성 영상에서 Zero-shot 성능이 불안정할 수 있음

권장 결합:

```text
YOLO-World Box
       ↓
SAM2 Box Prompt
       ↓
Instance Mask
       ↓
Metric Depth
       ↓
3D CollisionObject
```

YOLO-World는 `yolov8s-worldv2.pt`가 Export와 재학습 측면에서 수업용으로 적합하다.

## 13. Open-Vocabulary Segmentation

환경에 따라 Open-Vocabulary Instance Segmentation 모델을 사용할 수도 있다.

후보:

- YOLOE 계열
- Grounded SAM2
- Florence-2 + SAM2
- Grounding DINO + SAM2

이 방식은 `red box`, `wood block`, `plastic cube` 같은 텍스트 대상을 찾고 Mask를 만들 수 있다.

그러나 다음 이유로 기본 과정에는 무겁다.

- 여러 모델 설치 필요
- GPU Memory 증가
- ROS 2 실시간 통합 복잡
- 모델 라이선스와 버전 호환 확인 필요

고급 프로젝트에서만 선택한다.

## 14. Custom YOLO Segmentation 학습

빨간 공, ArUco 박스, 블록과 같은 수업 전용 물체를 안정적으로 인식하려면 Custom 학습이 가장 확실하다.

권장 클래스:

```yaml
names:
  0: red_ball
  1: aruco_box
  2: wooden_block
  3: plastic_cube
```

전이학습:

```python
from ultralytics import YOLO

model = YOLO("yolo26n-seg.pt")
model.train(
    data="manipulator_objects.yaml",
    epochs=50,
    imgsz=640,
    batch=8,
)
```

이전 버전 환경에서는 설치된 버전과 호환되는 `yolov8n-seg.pt` 또는 `yolo11n-seg.pt`를 기반으로 학습한다.

## 15. Gazebo 합성 데이터 자동 생성

Gazebo는 Custom 모델 학습용 데이터 생성에 유리하다.

```text
물체 Pose 무작위 변경
카메라 Pose 무작위 변경
조명 밝기·방향 변경
배경·바닥 Texture 변경
물체 색상 변경
        ↓
RGB Image 저장
        ↓
Segmentation Ground Truth 생성
        ↓
YOLO Polygon Label 변환
```

가능한 Ground Truth 생성 방법:

1. Gazebo Segmentation Camera Sensor 사용
2. 물체별 고유 Material Color로 별도 렌더링
3. RGB 영상과 Instance ID 영상 동시 저장
4. Mask를 Polygon으로 변환

Domain Randomization 항목:

- 조명
- 카메라 노이즈
- Exposure
- Texture
- 배경
- 물체 크기
- 회전
- 위치
- 일부 가림

실제 카메라 영상 50~200장을 추가 Fine-tuning하면 Sim-to-Real 성능을 개선할 수 있다.

---

# Part 4. Metric Depth와 3D 장애물 계산

## 16. Depth Anything V2 Metric 구성

```text
RGB Image
  ├─ YOLO Segmentation → Instance Mask
  └─ Depth Anything V2 Metric → Metric Depth
                            ↓
                  Mask 내부 Depth 선택
                            ↓
                  CameraInfo로 XYZ 계산
```

권장 ROS 2 출력:

```text
Topic   : /depth_anything/depth_metric
Type    : sensor_msgs/msg/Image
Encoding: 32FC1
Unit    : meter
Frame ID: camera_optical_frame
```

OpenMANIPULATOR-X 작업 공간의 초기 범위:

```text
minimum_depth: 0.08 m
maximum_depth: 1.20 m
```

## 17. Depth Mask를 3D Point로 변환

```python
import numpy as np


def depth_mask_to_points(
    depth: np.ndarray,
    mask: np.ndarray,
    fx: float,
    fy: float,
    cx: float,
    cy: float,
) -> np.ndarray:
    valid = (
        mask.astype(bool)
        & np.isfinite(depth)
        & (depth > 0.08)
        & (depth < 1.20)
    )

    v, u = np.nonzero(valid)
    z = depth[v, u]
    x = (u.astype(np.float32) - cx) * z / fx
    y = (v.astype(np.float32) - cy) * z / fy

    return np.stack((x, y, z), axis=1)
```

Mask의 가장자리에는 배경 Depth가 섞이기 쉬우므로 Erosion 후 사용한다.

## 18. MoGe-2 ViT-S 구성

```text
RGB Image
  ├─ YOLO Segmentation → Instance Mask
  └─ MoGe-2 → Point Map + Depth + Valid Mask
                            ↓
                   Instance Mask와 결합
                            ↓
                   3D Point 직접 추출
```

```python

def moge_mask_to_points(
    instance_mask: np.ndarray,
    point_map: np.ndarray,
    valid_mask: np.ndarray,
) -> np.ndarray:
    selected = (
        instance_mask.astype(bool)
        & valid_mask.astype(bool)
        & np.isfinite(point_map).all(axis=2)
    )
    return point_map[selected]
```

모델 출력 Point Map의 축 방향과 단위를 공식 정의로 확인해야 한다.

## 19. 이상점 제거와 3D Box

```python

def robust_filter(points: np.ndarray) -> np.ndarray:
    if len(points) < 100:
        return np.empty((0, 3), dtype=np.float32)

    median_z = np.median(points[:, 2])
    points = points[
        np.abs(points[:, 2] - median_z) < 0.12
    ]

    lower = np.percentile(points, 5, axis=0)
    upper = np.percentile(points, 95, axis=0)

    keep = np.all(
        (points >= lower) & (points <= upper),
        axis=1,
    )
    return points[keep]


def points_to_box(points: np.ndarray):
    minimum = points.min(axis=0)
    maximum = points.max(axis=0)
    center = (minimum + maximum) * 0.5
    size = maximum - minimum

    safety_margin = np.array([0.03, 0.03, 0.03])
    size = np.maximum(size + safety_margin, 0.03)
    return center, size
```

## 20. 알려진 물체 크기를 이용한 보정

COCO Class를 검출했다면 Class별 예상 크기 범위를 적용할 수 있다.

```yaml
object_size_limits:
  bottle:
    min: [0.04, 0.04, 0.08]
    max: [0.10, 0.10, 0.25]
  cup:
    min: [0.05, 0.05, 0.05]
    max: [0.14, 0.14, 0.18]
  apple:
    min: [0.05, 0.05, 0.05]
    max: [0.12, 0.12, 0.12]
```

추정 Box가 범위를 크게 벗어나면 다음 중 하나로 처리한다.

- 이전 Frame 값 유지
- Class 기본 크기 적용
- 검출을 `UNCERTAIN`으로 변경
- Collision Margin을 확대

---

# Part 5. MoveIt Planning Scene Monitor 통합

## 21. TF2 변환

Mask Point는 카메라 기준이다. Point 집합 전체를 `base_link`로 변환한 후 AABB를 다시 계산하는 것이 가장 안정적이다.

```text
Camera Frame PointCloud
      ↓
TF2: image timestamp
      ↓
Base Frame PointCloud
      ↓
AABB 계산
```

## 22. CollisionObject 갱신

```python
collision_object.id = f"{class_name}_{track_id}"
collision_object.header.frame_id = "base_link"
collision_object.operation = CollisionObject.ADD

primitive.type = SolidPrimitive.BOX
primitive.dimensions = [
    float(size_x),
    float(size_y),
    float(size_z),
]
```

갱신 정책:

- 같은 Track ID는 Pose와 크기 갱신
- 새 ID는 Scene에 추가
- 일정 시간 미검출 시 REMOVE
- 위치 변화가 2 cm 미만이면 발행 생략
- Mask가 화면 경계에 잘리면 크기 갱신 제한
- Confidence가 낮으면 기존 위치 유지

## 23. PointCloud2와 OctoMap

복잡한 Mask 형상을 Box로 단순화하지 않으려면 PointCloud를 발행한다.

```text
Mask PointCloud
      ↓
/obstacles/dynamic_points
      ↓
PointCloudOctomapUpdater
      ↓
Planning Scene OctoMap
```

동적 물체는 과거 Voxel이 남을 수 있으므로 일반적으로 CollisionObject 방식이 관리하기 쉽다.

## 24. 권장 혼합 구조

```text
정적 배경
  → Metric Depth
  → Robot TF + TSDF
  → PointCloud
  → OctoMap

동적 물체
  → YOLO Segmentation
  → Metric Depth 또는 Point Map
  → CollisionObject
  → Timeout 갱신

ArUco 박스
  → ArUco + solvePnP
  → 정확한 CollisionObject
```

---

# Part 6. 수업용 최종 권장안

## 25. 가장 쉬운 실습

```text
물체: bottle, cup, apple, orange
모델: 공식 nano segmentation 모델
Depth: Depth Anything V2 Metric Indoor
MoveIt: AABB CollisionObject
```

목표:

- 기본 사전학습 모델만으로 빠르게 성공
- Mask와 Depth Fusion 이해
- Planning Scene 갱신 확인

## 26. Gazebo 중심 실습

```text
물체:
YCB apple, orange, banana, mug, bowl
또는 검증된 Fuel 자산

모델:
공식 nano/small segmentation 모델

주의:
Texture와 조명을 실제 영상에 가깝게 설정
```

Gazebo의 단순 Primitive만으로 COCO YOLO가 검출되지 않으면 실패가 아니라 Domain Gap의 사례로 설명한다.

## 27. 빨간 공 실습

```text
검출: HSV + Hough Circle
Mask: HSV
Depth: Depth Anything V2 또는 MoGe-2
MoveIt: Sphere 또는 Box CollisionObject
```

YOLO는 선택적 비교 항목으로 둔다.

## 28. ArUco 박스 실습

```text
검출·Pose: ArUco + solvePnP
크기: 사전에 알고 있는 Box 크기
MoveIt: CollisionObject
```

고급 확장:

```text
Custom YOLO-Seg로 ArUco 박스 전체 Mask
        +
ArUco Pose를 Ground Truth로 사용
        +
Metric Depth 결과 정확도 비교
```

## 29. Custom 학습 프로젝트

```text
Gazebo 합성 데이터
        +
실제 카메라 소량 데이터
        ↓
red_ball / aruco_box / block 학습
        ↓
YOLO Segmentation
        ↓
Metric Depth
        ↓
MoveIt Scene Update
```

이 프로젝트는 AI 활용 코드 생성, 데이터 생성, 학습, ROS 2, MoveIt을 모두 연결할 수 있다.

---

## 30. 모델 선택 결론

| 목표 | 추천 방식 |
| --- | --- |
| 바로 성공하는 수업 | COCO Seg + bottle/cup/apple/orange |
| 빨간 공 | HSV·Hough, 필요 시 Custom YOLO |
| ArUco 박스 | ArUco + solvePnP |
| 일반 박스·블록 탐색 | YOLO-World 또는 Grounded SAM2 |
| 박스·블록 정밀 Mask | Custom YOLO Segmentation |
| Gazebo 중심 학습 | YCB/Fuel + Domain Randomization |
| MoveIt 실시간 동적 장애물 | Segmentation + Metric Depth + CollisionObject |
| 정적 주변 환경 | Robot TF + Metric Depth + TSDF + OctoMap |

최종적으로 수업의 기본 모델은 **공식 nano Segmentation 모델**, 기본 물체는 **병·컵·사과·오렌지**를 추천한다. 빨간 공과 ArUco 박스는 YOLO에 억지로 맞추지 않고 각각 HSV/Hough와 ArUco Pose Estimation을 사용하는 것이 더 논리적이다. Custom YOLO 학습은 4주차 고급 프로젝트로 운영한다.

---

## 31. 평가 기준

| 평가 항목 | 기준 | 배점 |
| --- | --- | ---: |
| 물체 선정 | 모델 Class와 실제 물체의 적합성 설명 | 10 |
| Segmentation | Instance Mask와 Confidence 생성 | 15 |
| Metric Depth | meter 단위 Depth 또는 Point Map 생성 | 15 |
| 3D Fusion | Mask 내부 3D Point와 Box 계산 | 20 |
| TF 변환 | Base Frame에서 물체 위치 유지 | 15 |
| MoveIt 통합 | CollisionObject 또는 OctoMap 갱신 | 15 |
| 안정화 | Filter·Timeout·Safety Margin 적용 | 5 |
| 문서화 | 모델·Gazebo·한계 비교 | 5 |
| **합계** |  | **100** |

---

## 32. 안전 주의사항

- 단안 Metric Depth는 안전 인증 센서가 아니다.
- 실제 물체보다 큰 Collision Margin을 적용한다.
- 투명·반사·검정 물체의 Depth 결과를 신뢰하지 않는다.
- 새 장애물이 검출되면 실행 중 Trajectory를 중지하는 별도 로직을 둔다.
- Gazebo와 RViz에서 먼저 검증한다.
- 실제 로봇은 저속으로 운용한다.

---

## 33. 참고 자료

- Ultralytics COCO Segmentation Dataset 문서
- Ultralytics Instance Segmentation 문서
- Ultralytics YOLO-World 문서
- Gazebo Fuel Model Insertion 문서
- YCB Object and Model Set
- Depth Anything V2 Metric 공식 저장소
- Microsoft MoGe 공식 저장소
- MoveIt Planning Scene Monitor 문서
- MoveIt Occupancy Map Monitor 문서
- ROS 2 TF2 문서
