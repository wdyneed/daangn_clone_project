function previewImage(event) {
  let reader = new FileReader();
  reader.onload = function () {
    let output = document.getElementById("imagePreview");
    output.src = reader.result;
    output.classList.add("img-upload-fit");
  };
  reader.readAsDataURL(event.target.files[0]);
}
function uploadImage() {
  const input = document.getElementById('images');
  const preview = document.getElementById('imagePreview');

  // 선택한 이미지 파일
  const files = input.files;

  // 이미지를 서버로 업로드하기 위한 FormData 생성
  const formData = new FormData();

  // 모든 선택한 이미지 파일을 FormData에 추가
  for (let i = 0; i < files.length; i++) {
    formData.append('images', files[i]);
  }

  // 서버 엔드포인트 URL을 실제로 사용 가능한 URL로 수정해야 합니다.
  const url = `/api/post/${postPk}/images/`; // post_id 변수가 이미지를 연결할 포스트 ID를 가지고 있어야 합니다.

  // POST 요청을 보내기 위한 XMLHttpRequest
  const xhr = new XMLHttpRequest();

  // POST 요청 설정
  xhr.open('POST', url, true);

  // POST 요청 완료 후의 콜백 함수
  xhr.onreadystatechange = function () {
    if (xhr.readyState === 4) {
      if (xhr.status === 201) {
        // 업로드 성공 시 서버에서 반환한 응답을 처리
        const response = JSON.parse(xhr.responseText);
        console.log('이미지 업로드 성공:', response);
      } else {
        // 업로드 실패 시 오류 처리
        console.error('이미지 업로드 실패');
      }
    }
  };

  // POST 요청 전송
  xhr.send(formData);
}