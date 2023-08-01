example.env 파일의 예시를 보고 값을 적당히 채워넣기 -> 주석 없애기 -> cp example.env .env

가상환경 설정.
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
pip install --upgrade clickhouse-connect==0.5.22  ->  (Unable to connect optimized C data functions [No module named '_testbuffer'], falling back to pure Python 문제 해결)

chroma Lib의 chroma.py 124줄 n_results=n_results -> n_results=int(n_results) 로 수정함.

Slack Event 로컬에서 테스트 하는 법 (https://yunwoong.tistory.com/135 참고)
ngrok 다운
ngrok 실행 -> ngrok http 5001 입력 엔터 -> url (https://api.slack.com/apps/A05FXCD3NES/event-subscriptions?) 여기로 가서 Request URL에 등록하면 됨