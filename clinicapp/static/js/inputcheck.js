function validatePassword() {
  var passwordInput = document.getElementById("password");
  var password = passwordInput.value;
  var pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*?[~`!@#$%\^&*()\-_=+[\]{};:\x27.,\x22\\|/?><]).{8,}$/;

  var divPass = document.getElementById('div-password');
  var cidError = document.getElementById('cid-error');
  if (cidError)
  {
      cidError.remove();
  }

  if (password != "" && !pattern.test(password)) {
    var divError = document.createElement('div');
    divError.setAttribute('id', 'cid-error');
    divError.setAttribute('class', 'alert alert-danger mt-2');
    divError.innerHTML = 'Mật khẩu phải chứa ít nhất 1 chữ thường, 1 chữ hoa, 1 số, 1 ký tự đặc biệt và ít nhất 8 ký tự!!!';
    divPass.appendChild(divError);
    passwordInput.value="";
  }

}

