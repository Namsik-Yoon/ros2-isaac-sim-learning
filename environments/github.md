# GitHub 연결과 매일 기록

공개 저장소는 [Namsik-Yoon/ros2-isaac-sim-learning](https://github.com/Namsik-Yoon/ros2-isaac-sim-learning)입니다. 기본 브랜치는 `main`이며, 원본 작업 폴더의 `origin`이 이 저장소를 가리킵니다. 개인 평가와 답변은 `.learning/`에 두고 Git 추적에서 제외합니다.

## 첫 연결

다른 사람은 아래 명령으로 저장소를 내려받고 README의 준비 절차를 따릅니다. 자신의 GitHub에 변경을 올리려면 먼저 자신의 계정으로 fork하고 해당 fork를 복제합니다.

```bash
git clone https://github.com/Namsik-Yoon/ros2-isaac-sim-learning.git
cd ros2-isaac-sim-learning
```

기존 작업 폴더에서는 `git remote -v`로 연결을 확인합니다. 기존 원격 저장소에 다른 변경이 있으면 먼저 상태를 확인하고 합칩니다. 강제 push로 덮어쓰지 않습니다.

## 매일 마무리

1. `study-log/TEMPLATE.md`를 날짜별 파일로 복사합니다.
2. 직접 한 일, 예상과 실제 차이, 실패 원인, 본인 설명을 적습니다.
3. `git diff`로 변경 내용과 공개할 정보를 확인합니다.
4. 해당 코드와 학습일지만 선택해 커밋하고 연결된 원격에 push합니다.
5. 큰 실습을 실제 재현한 시점에 태그를 남깁니다.

인프라 구축 커밋은 학습자가 실습을 끝냈다는 의미가 아닙니다. 대용량 설치 파일이나 센서 데이터는 Git에 넣지 않습니다. 학습·재사용 범위를 정할 라이선스는 아직 지정하지 않았습니다.
