function validatePassword() {
  var passwordInput = document.getElementById("password");
  var password = passwordInput.value;
  var pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*?[~`!@#$%\^&*()\-_=+[\]{};:\x27.,\x22\\|/?><]).{8,}$/;

  if (password != "" && !pattern.test(password)) {
    alert("Mật khẩu phải chứa ít nhất 1 chữ thường, 1 chữ hoa, 1 số, 1 ký tự đặc biệt và ít nhất 8 ký tự");
    passwordInput.value="";
    return false;
  }

  // Xử lý logic tiếp theo khi mật khẩu hợp lệ
}

