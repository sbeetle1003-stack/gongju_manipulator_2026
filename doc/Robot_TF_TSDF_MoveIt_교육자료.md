# Robot TF + TSDF 기반 3차원 환경 재구성과 MoveIt 통합 교육자료

## 1. 교육 목표

이 교육자료는 OpenMANIPULATOR-X 끝단에 장착된 단안 카메라와 로봇 TF를 이용하여 주변 환경을 3차원으로 재구성하고, 재구성 결과를 MoveIt의 Planning Scene Monitor에 반영하는 과정을 다룬다.

학습자는 다음 내용을 이해하고 구현한다.

- 로봇 Forward Kinematics와 TF를 이용한 카메라 자세 획득
- 단안 카메라 영상에서 Metric Depth 생성
- RGB 영상과 Depth 영상을 이용한 RGB-D Frame 구성
- 여러 시점의 RGB-D Frame을 TSDF Volume에 누적
- TSDF에서 PointCloud 또는 Mesh 추출
- PointCloud2 발행
- MoveIt Occupancy Map Monitor와 OctoMap 갱신
- 정적 환경과 동적 장애물의 분리
- 실시간 재구성에서 발생하는 좌표계·시간·노이즈 문제 해결

---

## 2. 핵심 개념

### 2.1 로봇 TF를 사용하는 이유

일반적인 SLAM 시스템은 영상에서 카메라의 위치와 환경 지도를 동시에 추정한다. 그러나 카메라가 로봇팔 끝단에 고정되어 있다면 카메라 자세는 로봇 관절 상태와 URDF를 통해 이미 계산할 수 있다.

```text
/joint_states
      ↓
robot_state_publisher
      ↓
/tf, /tf_static
      ↓
base_link → camera_optical_frame
```

따라서 영상만으로 카메라 Pose를 다시 추정하는 ORB-SLAM보다 다음 구조가 단순하고 실제 미터 단위를 유지하기 쉽다.

```text
Robot TF의 정확한 Camera Pose
             +
단안 영상에서 추정한 Metric Depth
             ↓
TSDF Volume Integration
```

### 2.2 TSDF란

TSDF는 Truncated Signed Distance Function의 약자다. 3차원 공간을 Voxel로 나누고 각 Voxel에 가장 가까운 표면까지의 부호 있는 거리를 저장한다.

- 표면 앞쪽: 양수 또는 자유 공간
- 표면 뒤쪽: 음수 또는 점유 공간
- 표면: 0에 가까운 값
- 일정 거리 밖: Truncation 범위로 제한

여러 프레임의 깊이 정보를 누적하면 단일 Depth Frame의 노이즈가 평균화되고 표면이 더 부드럽게 재구성된다.

Open3D의 TSDF Integration은 알려진 카메라 자세와 Depth Image를 Voxel Volume에 통합하여 Dense Reconstruction을 수행한다.

### 2.3 TSDF와 OctoMap의 차이

| 구분 | TSDF | OctoMap |
| --- | --- | --- |
| 주요 목적 | 표면 재구성 | 점유·비점유 공간 표현 |
| 저장 값 | 표면까지의 거리 | 점유 확률 |
| 결과 | Mesh, PointCloud | Occupancy Voxel |
| 장점 | 매끄러운 표면 | 충돌 검사에 적합 |
| MoveIt 연계 | PointCloud로 변환 후 연계 | Planning Scene에서 직접 사용 |

권장 파이프라인은 TSDF를 환경 재구성에 사용하고, 추출한 PointCloud를 MoveIt의 OctoMap Updater에 전달하는 방식이다.

---

## 3. 전체 시스템 구조

```text
/camera/image_raw
/camera/camera_info
/joint_states
/tf
/tf_static
        ↓
metric_depth_node
        ├─ Depth Anything V2 Metric
        └─ MoGe-2 Metric Point Map
        ↓
/depth/image_metric
        ↓
tsdf_reconstruction_node
        ├─ CameraInfo
        ├─ base_link → camera_optical_frame TF
        ├─ RGB-D Frame 생성
        ├─ TSDF Integration
        └─ PointCloud 추출
        ↓
/reconstruction/points
        ↓
MoveIt PointCloudOctomapUpdater
        ↓
PlanningSceneMonitor
        ↓
OctoMap Collision Geometry
        ↓
경로 계획 및 충돌 회피
```

---

## 4. 좌표계 설계

### 4.1 권장 Frame

```text
base_link
 └─ link1
    └─ link2
       └─ link3
          └─ link4
             └─ camera_link
                └─ camera_optical_frame
```

OpenCV와 일반 카메라 Optical Frame은 보통 다음 축을 사용한다.

```text
X: 영상 오른쪽
Y: 영상 아래쪽
Z: 카메라 전방
```

TSDF에 통합할 때 모든 Frame은 하나의 기준 좌표계로 정렬되어야 한다. MoveIt과 연결하려면 `base_link` 또는 MoveIt Planning Frame을 World Frame으로 사용하는 것이 가장 단순하다.

### 4.2 필요한 TF

```text
T_base_camera = lookup_transform(
    target_frame="base_link",
    source_frame="camera_optical_frame",
    time=image_stamp
)
```

영상이 촬영된 시각의 TF를 사용해야 한다. 최신 TF만 사용하면 로봇팔이 움직이는 동안 영상과 자세가 어긋나 재구성 표면이 번지거나 이중으로 나타난다.

---

## 5. 필요한 입력 데이터

### 5.1 카메라 영상

```text
Topic: /camera/image_raw
Type : sensor_msgs/msg/Image
```

### 5.2 카메라 내부 파라미터

```text
Topic: /camera/camera_info
Type : sensor_msgs/msg/CameraInfo
```

주요 값:

```text
fx = K[0]
fy = K[4]
cx = K[2]
cy = K[5]
```

### 5.3 카메라 자세

```text
/tf
/tf_static
```

### 5.4 Metric Depth

```text
Topic: /depth/image_metric
Type : sensor_msgs/msg/Image
Encoding 권장: 32FC1
단위: meter
```

---

## 6. 단안 영상에서 Metric Depth 만들기

단안 카메라 자체는 절대 깊이를 직접 측정하지 않는다. 따라서 다음 중 하나가 필요하다.

1. Depth Anything V2 Metric
2. MoGe-2 Metric Depth 또는 Point Map
3. 알려진 물체 크기를 이용한 기하학적 거리 추정
4. 다중 시점 삼각측량

TSDF 교육 실습에서는 모델 실행이 간단한 Metric Depth 모델을 우선 사용하고, 확장 실습에서 ORB Matching과 Triangulation을 비교한다.

---

## 7. Depth Image에서 3D Point 계산

각 픽셀 `(u, v)`와 깊이 `Z`를 이용해 카메라 좌표계의 3차원 점을 계산한다.

```text
X = (u - cx) × Z / fx
Y = (v - cy) × Z / fy
Z = depth(u, v)
```

이 점은 `camera_optical_frame` 기준이므로 TF를 이용해 `base_link` 기준으로 변환한다.

```text
P_base = T_base_camera × P_camera
```

TSDF Library를 사용하는 경우에는 Depth Image, Camera Intrinsic, Camera Extrinsic을 Volume Integrator에 전달한다.

---

## 8. Open3D TSDF 구성

### 8.1 설치

```bash
pip install open3d
```

### 8.2 기본 Volume 생성

```python
import open3d as o3d

volume = o3d.pipelines.integration.ScalableTSDFVolume(
    voxel_length=0.01,
    sdf_trunc=0.04,
    color_type=(
        o3d.pipelines.integration.TSDFVolumeColorType.RGB8
    ),
)
```

OpenMANIPULATOR-X 작업 공간 권장 초기값:

```text
voxel_length: 0.01 ~ 0.03 m
sdf_trunc   : voxel_length의 약 3~5배
max_depth   : 0.8 ~ 1.5 m
integration : 2~5 Hz
```

### 8.3 Camera Intrinsic 생성

```python
intrinsic = o3d.camera.PinholeCameraIntrinsic(
    width,
    height,
    fx,
    fy,
    cx,
    cy,
)
```

### 8.4 RGB-D Frame 생성

```python
color_o3d = o3d.geometry.Image(rgb_image)
depth_o3d = o3d.geometry.Image(depth_image.astype("float32"))

rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(
    color_o3d,
    depth_o3d,
    depth_scale=1.0,
    depth_trunc=1.2,
    convert_rgb_to_intensity=False,
)
```

Depth Image가 meter 단위의 `float32`이면 `depth_scale=1.0`으로 설정한다.

### 8.5 TSDF Integration

Open3D Integration 함수의 Extrinsic은 구현 버전에 따라 World-to-Camera Transform을 요구한다. TF에서 얻은 값이 Camera-to-World라면 역행렬을 전달해야 한다.

```python
camera_to_world = transform_to_matrix(tf_msg)
world_to_camera = np.linalg.inv(camera_to_world)

volume.integrate(
    rgbd,
    intrinsic,
    world_to_camera,
)
```

### 8.6 PointCloud 추출

```python
point_cloud = volume.extract_point_cloud()
point_cloud = point_cloud.voxel_down_sample(0.02)
```

### 8.7 Mesh 추출

```python
mesh = volume.extract_triangle_mesh()
mesh.compute_vertex_normals()
```

MoveIt에는 Mesh 전체를 자주 갱신하기보다 PointCloud를 OctoMap Updater에 전달하는 방식이 더 단순하다.

---

## 9. ROS 2 Node 구성

### 9.1 권장 Node

```text
metric_depth_node
    입력: /camera/image_raw
    출력: /depth/image_metric

tsdf_reconstruction_node
    입력: /camera/image_raw
          /depth/image_metric
          /camera/camera_info
          /tf
    출력: /reconstruction/points
          /reconstruction/mesh_marker
          /reconstruction/status
```

### 9.2 동기화

RGB와 Depth는 같은 원본 영상에서 생성되므로 Header Stamp를 유지해야 한다.

권장 방식:

- Depth Node가 입력 Image Header를 그대로 복사
- `message_filters.ApproximateTimeSynchronizer` 사용
- Image Stamp 시점의 TF Lookup

### 9.3 TSDF Node 코드 골격

```python
class TsdfReconstructionNode(Node):
    def __init__(self):
        super().__init__("tsdf_reconstruction")

        self.bridge = CvBridge()
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(
            self.tf_buffer,
            self,
        )

        self.volume = create_tsdf_volume()
        self.intrinsic = None
        self.last_integration_time = None

        # RGB, Depth, CameraInfo 구독
        # PointCloud2 Publisher 생성

    def synchronized_callback(
        self,
        color_msg,
        depth_msg,
    ):
        # 1. 영상 변환
        # 2. CameraInfo 확인
        # 3. 해당 timestamp의 TF 조회
        # 4. 움직임이 충분한지 확인
        # 5. Depth 유효 범위 필터
        # 6. TSDF에 Integration
        # 7. 일정 주기마다 PointCloud 추출·발행
        pass
```

---

## 10. 모든 프레임을 적분하지 않는 이유

카메라가 거의 움직이지 않은 상태에서 모든 프레임을 통합하면 같은 관측이 과도하게 누적되고 처리량만 증가한다.

권장 적분 조건:

```text
이전 적분 자세와 비교하여
이동 거리 > 0.01 ~ 0.03 m
또는
회전 변화 > 2 ~ 5 degree
```

또한 다음 경우에는 적분하지 않는다.

- TF 조회 실패
- Depth 유효 픽셀 비율 부족
- Depth 값이 대부분 최대 범위에 있음
- 로봇이 빠르게 움직이는 중
- Motion Blur 발생
- Confidence가 낮음

---

## 11. PointCloud2 발행

TSDF에서 추출한 PointCloud는 `base_link` 기준으로 발행한다.

```text
Topic   : /reconstruction/points
Type    : sensor_msgs/msg/PointCloud2
Frame ID: base_link
```

권장 필터:

- Workspace Crop
- Voxel Downsampling
- Statistical Outlier Removal
- Radius Outlier Removal
- 바닥·작업대 Plane 선택적 제거
- 로봇 자체 형상 제거

---

## 12. MoveIt Occupancy Map Monitor 연결

### 12.1 sensors_3d.yaml 예시

```yaml
sensors:
  - point_cloud_sensor

point_cloud_sensor:
  sensor_plugin: occupancy_map_monitor/PointCloudOctomapUpdater
  point_cloud_topic: /reconstruction/points
  max_range: 1.5
  point_subsample: 1
  padding_offset: 0.02
  padding_scale: 1.0
  filtered_cloud_topic: /reconstruction/filtered_points
  max_update_rate: 5.0
```

### 12.2 MoveIt 설정

```python
moveit_config = (
    MoveItConfigsBuilder(
        "open_manipulator_x",
        package_name="open_manipulator_x_moveit_config",
    )
    .sensors_3d(file_path="config/sensors_3d.yaml")
    .to_moveit_configs()
)
```

### 12.3 확인 Topic

```bash
ros2 topic echo /monitored_planning_scene
ros2 topic hz /reconstruction/points
ros2 topic echo /reconstruction/status
```

RViz의 MotionPlanning Display에서 Scene Geometry와 OctoMap 표시를 활성화한다.

---

## 13. 로봇 자체가 점군에 포함되는 문제

끝단 카메라 영상에는 그리퍼나 링크가 보일 수 있다. 이 점이 OctoMap에 들어가면 MoveIt이 로봇과 자기 자신이 충돌한다고 판단할 수 있다.

해결 방법:

1. 카메라 영상에서 고정된 로봇 ROI를 Mask 처리
2. 현재 Robot State의 Collision Geometry와 겹치는 점 제거
3. 그리퍼 주변 일정 반경 제거
4. MoveIt Self-filter 사용 가능 여부 확인
5. 작업 공간 외부 점 제거

---

## 14. 정적 환경과 동적 장애물 분리

TSDF는 정적 환경을 누적하는 데 적합하다. 움직이는 사람이나 물체를 계속 적분하면 과거 위치가 잔상으로 남는다.

권장 구조:

```text
정적 환경
  → Metric Depth
  → TSDF
  → OctoMap

동적 물체
  → YOLO Segmentation
  → Mask + Depth
  → 개별 CollisionObject
  → 짧은 Timeout으로 실시간 갱신
```

YOLO에서 사람·이동 물체로 판단된 Mask는 TSDF 적분에서 제외한다.

---

## 15. 실습 단계

### 실습 1. TF와 카메라 Pose 확인

- 로봇팔을 여러 자세로 이동
- `base_link → camera_optical_frame` TF 출력
- Translation과 Quaternion 기록
- 영상 Stamp 기준 TF Lookup

### 실습 2. 단일 Depth Frame의 PointCloud 생성

- Metric Depth 추론
- CameraInfo로 3D Point 계산
- PointCloud2 발행
- RViz 표시

### 실습 3. 다중 시점 TSDF 적분

- 로봇팔을 5~10개 자세로 이동
- 각 자세의 RGB·Depth·TF 적분
- PointCloud 추출
- 단일 Frame 점군과 비교

### 실습 4. MoveIt OctoMap 통합

- `/reconstruction/points`를 Occupancy Map Monitor에 연결
- RViz Planning Scene에서 장애물 확인
- 장애물 추가 전후 경로 계획 비교

### 실습 5. 동적 장애물 제외

- YOLO Segmentation으로 사람 또는 이동 물체 Mask 생성
- 해당 Mask를 TSDF 적분에서 제외
- 개별 CollisionObject로 별도 갱신

---

## 16. 미니 프로젝트

### 프로젝트 A. 작업대 자동 재구성

- 로봇팔이 미리 정한 8개 View Point를 순회
- 각 시점의 RGB·Depth·TF 적분
- 작업대와 고정 장애물 PointCloud 생성
- MoveIt OctoMap에 반영
- 동일 목표의 경로가 장애물을 피해 변경되는지 확인

### 프로젝트 B. Scan Before Plan

```text
HOME
  ↓
SCAN_LEFT
  ↓
SCAN_CENTER
  ↓
SCAN_RIGHT
  ↓
TSDF 생성
  ↓
OctoMap 갱신
  ↓
MoveIt Plan
  ↓
Execute
```

### 프로젝트 C. 정적·동적 장애물 혼합 작업 셀

- TSDF: 테이블, 벽, 고정 박스
- YOLO + Depth: 사람, 이동 박스
- OctoMap과 CollisionObject 동시 사용
- 위험 물체가 접근하면 실행 정지

---

## 17. 평가 기준

| 평가 항목 | 기준 | 배점 |
| --- | --- | ---: |
| TF 이해 | 영상 시점의 Camera Pose를 정확히 획득 | 15 |
| Metric Depth | meter 단위 Depth Image 생성 | 15 |
| TSDF 통합 | 여러 시점의 RGB-D를 안정적으로 누적 | 20 |
| PointCloud | 필터링된 PointCloud2 발행 | 15 |
| MoveIt 통합 | OctoMap이 Planning Scene에 반영 | 20 |
| 검증 | 장애물 반영 전후 경로 비교 | 10 |
| 문서화 | 구성도·실행 방법·한계 정리 | 5 |
| **합계** |  | **100** |

---

## 18. 주요 오류와 점검 사항

### 표면이 두 겹으로 보임

- 영상과 TF Timestamp 불일치
- Hand-Eye Calibration 오류
- Depth Scale 오류
- Robot Joint State 지연

### 환경이 흔들림

- 단안 Metric Depth의 프레임별 Scale 변화
- 로봇팔 진동
- Motion Blur
- 지나치게 작은 Voxel

### OctoMap에 로봇이 장애물로 나타남

- Self-filter 미적용
- 그리퍼 ROI 미제거
- TF Frame 오류

### 장애물이 사라지지 않음

- Occupied Point만 넣고 Free Space Ray를 갱신하지 않음
- 누적 PointCloud를 계속 전체 발행
- 동적 물체를 TSDF에 적분함

---

## 19. 안전 주의사항

- 단안 Depth와 TSDF 결과만으로 산업 안전을 보장할 수 없다.
- 실제 장비에서는 저속 동작과 비상 정지 장치를 사용한다.
- Collision Padding을 충분히 적용한다.
- Planning Scene 갱신과 실행 중 Trajectory 중지는 별도 문제다.
- 새 장애물이 나타났을 때 Controller 정지 또는 Trajectory Cancel 로직을 추가한다.
- 실제 로봇 적용 전 Gazebo와 RViz에서 검증한다.

---

## 20. 참고 자료

- Open3D TSDF Integration 공식 문서
- Open3D ScalableTSDFVolume 예제
- MoveIt Planning Scene Monitor 및 Occupancy Map Monitor 문서
- ROS 2 TF2 문서
- Depth Anything V2 Metric 공식 저장소
- Microsoft MoGe 공식 저장소
