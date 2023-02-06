## Custom Recorder  
<br>
HomeAssistant 에서 엔티티의 변경 기록을 외부 파일에 저장하는 용도로 개발된 커스텀 컴포넌트입니다.
<br>
<br>
[설치방법]  

* HASC 에서 저장소 추가로 설치
* 소스코드를 직접 다운로드 받아 HA의 config/custom_component 폴더 하위에 저장소의 custom_component/custom_recorder 폴더를 복사 후 재시작

[설정방법]

* 통합구성요소 추가하기를 이용하여 Custom Recorder 를 추가
* 각 항목에 맞게 설정 후 추가를 완료하면 원본 엔티티의 값이 변경될 때 마다 HomeAssistant 의 config/custom_recorder/data 폴더에 파일을 생성하여 데이터가 기록 됨
<br/>
<br/>
![add_entity.jpg](https://github.com/oukene/custom_recorder/blob/main/images/add_entity.jpg)
