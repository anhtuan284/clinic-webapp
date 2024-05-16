const avatarInput = document.getElementById('avatar');
const avatarPreview = document.getElementById('avatar-preview');
// document.getElementsByTagName('form')[0].addEventListener('submit', validateForm)
document.getElementsByTagName('form')[0].addEventListener('submit', function (event) {
    validateForm(event); // Gọi hàm validateForm() như đã làm trước đó

    // Sau khi form đã được gửi đi và xử lý thành công, reset giá trị của biến formSubmitted thành false
});
avatarInput.onchange = () => {
    const file = avatarInput.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = () => {
            avatarPreview.src = reader.result;
        };
        reader.readAsDataURL(file);
    }
};

var formSubmitted = false;


function validateInput(input) {
    var errorElement = document.getElementById(input.id + '-error');
    if (!input.value) {
        input.classList.add('is-invalid');
        errorElement.style.display = 'block';
        return false;
    } else {
        input.classList.remove('is-invalid');
        errorElement.style.display = 'none';
        return true;
    }
}

function validateForm(event) {
    // var inputs = document.querySelectorAll('input[required]');
    // var isValid = true;
    // for (var i = 0; i < inputs.length; i++) {
    //     if (!validateInput(inputs[i])) {
    //         isValid = false;
    //     }

    //     // Kiểm tra mật khẩu hợp lệ
    //     if (inputs[i].id === 'password') {
    //         if (!validatePassword(inputs[i])) {
    //             isValid = false;
    //         }
    //     }

    //     // Kiểm tra tên đăng nhập hợp lệ
    //     if (inputs[i].id === 'username') {
    //         if (!validateUsername(inputs[i])) {
    //             isValid = false;
    //         }
    //     }
    // }
    // return isValid;
    var inputs = document.getElementsByClassName('form-control');
    if (!validateUsername(inputs[0], false)) {
        event.preventDefault();

    }
    if (!validatePassword(inputs[1], false)) {
        event.preventDefault();
    }
    if (!validateInput(inputs[2], false)) {
        event.preventDefault();
    }
    if (!validateInput(inputs[3], false)) {
        event.preventDefault();
    }
    if (!validateInput(inputs[4], false)) {
        event.preventDefault();
    }
    if (!validateEmail(inputs[5], false)) {
        event.preventDefault();
    }
    if (!validatePhone(inputs[6], false)) {
        event.preventDefault();
    }
    if (!validateCid(inputs[7], false)) {
        event.preventDefault();
    }
    if (!validateInput(inputs[8], false)) {
        event.preventDefault();
    }

    return true;

}

var input = document.getElementById('cid');
var formatted = false;

input.addEventListener('input', function (event) {
    var value = event.target.value;
    var divCid = document.getElementById('div-cid');
    var cidError = document.getElementById('cid-error');
    if (cidError) {
        cidError.remove();
    }

    if (isNaN(value)) {
        var divError = document.createElement('div');
        divError.setAttribute('id', 'cid-error');
        divError.setAttribute('class', 'alert alert-danger mt-2');
        divError.innerHTML = 'Chỉ được nhập dữ liệu số';
        divCid.appendChild(divError);
        event.target.value = ""; // Xóa giá trị đầu vào
    }

});

function validatePassword(input, fromSelf = true) {
    var password = input.value;
    var errorElement = document.getElementById('password-error');

    // Kiểm tra độ dài mật khẩu
    if (password.length < 9) {
        input.classList.add('is-invalid');
        if (fromSelf)
            errorElement.textContent = 'Mật khẩu phải có ít nhất 9 ký tự.';
        if (!fromSelf && errorElement.textContent == '')
            errorElement.textContent = 'Mật khẩu phải có ít nhất 9 ký tự.';
        errorElement.style.display = 'block';
        input.value = "";
        return false;
    }

    // Kiểm tra ký tự hoa
    if (!/[A-Z]/.test(password)) {
        input.classList.add('is-invalid');
        if (fromSelf)
            errorElement.textContent = 'Mật khẩu phải chứa ít nhất một ký tự viết hoa.';
        if (!fromSelf && errorElement.textContent == '')
            errorElement.textContent = 'Mật khẩu phải chứa ít nhất một ký tự viết hoa.';
        errorElement.style.display = 'block';
        input.value = "";
        return false;
    }

    // Kiểm tra chứa ít nhất 1 ký tự số
    if (!/\d/.test(password)) {
        input.classList.add('is-invalid');
        if (fromSelf)
            errorElement.textContent = 'Mật khẩu cần chứa ít nhất 1 số';
        if (!fromSelf && errorElement.textContent == '')
            errorElement.textContent = 'Mật khẩu cần chứa ít nhất 1 số';
        errorElement.style.display = 'block';
        input.value = "";
        return false;
    }

    // Kiểm tra ký tự đặc biệt
    if (!/[\W_]/.test(password)) {
        input.classList.add('is-invalid');
        if (fromSelf)
            errorElement.textContent = 'Mật khẩu phải chứa ít nhất một ký tự đặc biệt.';
        if (!fromSelf && errorElement.textContent == '')
            errorElement.textContent = 'Mật khẩu phải chứa ít nhất một ký tự đặc biệt.';
        errorElement.style.display = 'block';
        input.value = "";

        return false;
    }

    // Nếu mật khẩu hợp lệ, ẩn thông báo lỗi và trả về true
    input.classList.remove('is-invalid');
    errorElement.style.display = 'none';
    return true;
}

async function validateUsername(input, fromSelf = true) {
    var username = input.value;
    var errorElement = document.getElementById('username-error');

    // Kiểm tra độ dài username
    if (username.length < 6) {
        input.classList.add('is-invalid');
        if (fromSelf)
            errorElement.textContent = 'Tên đăng nhập phải có ít nhất 6 ký tự.';
        if (!fromSelf && errorElement.textContent == "")
            errorElement.textContent = 'Tên đăng nhập phải có ít nhất 6 ký tự.';
        errorElement.style.display = 'block';
        return false;
    }
    let flag = await checkUsername(username)
    if (flag === false) {
        errorElement.textContent = 'Tên đăng nhập đã tồn tại !';
        errorElement.style.display = 'block';
        return false
    }

    input.classList.remove('is-invalid');
    errorElement.style.display = 'none';
    return true;
}

function validateEmail(input, fromSelf = true) {
    var email = input.value;
    var errorElement = document.getElementById('email-error');

    //Kiểm tra trống
    if (email == "") {
        input.classList.add('is-invalid');
        if (fromSelf)
            errorElement.textContent = 'Vui lòng nhập email của bạn.';
        if (!fromSelf && errorElement.textContent == "")
            errorElement.textContent = 'Vui lòng nhập email của bạn.';
        errorElement.style.display = 'block';
        input.value = "";
        return false;
    } else if (/^(.+)@(.+)$/.test(email)) {
        input.classList.remove('is-invalid');
        errorElement.style.display = 'none';
        return true;
    }

    // Kiểm tra có @ không
    var regex = /^(.+)@$/;
    if (!regex.test(email)) {
        input.classList.add('is-invalid');
        if (fromSelf)
            errorElement.textContent = 'Email phải chứa ký tự @.';
        if (!fromSelf && errorElement.textContent == "")
            errorElement.textContent = 'Email phải chứa ký tự @.';
        errorElement.style.display = 'block';
        input.value = "";
        return false;
    }

    // Kiểm tra phần đằng sau @
    regex = /^(.+)@(.+)$/;
    if (!regex.test(email)) {
        input.classList.add('is-invalid');
        if (fromSelf)
            errorElement.textContent = 'Email thiếu phần sau @.';
        ;
        if (!fromSelf && errorElement.textContent == "")
            errorElement.textContent = 'Email thiếu phần sau @.';
        ;
        errorElement.style.display = 'block';
        input.value = "";
        return false;
    }

    input.classList.remove('is-invalid');
    errorElement.style.display = 'none';
    return true;
}

function validatePhone(input, fromSelf = true) {
    var phone = input.value;
    var errorElement = document.getElementById('phone-error');

    // Kiểm tra sdt trống
    if (phone == "") {
        input.classList.add('is-invalid');
        if (fromSelf)
            errorElement.textContent = 'Vui lòng nhập số điện thoại!';
        if (!fromSelf && errorElement.textContent == "")
            errorElement.textContent = 'Vui lòng nhập số điện thoại!';
        errorElement.style.display = 'block';
        input.value = "";
        return false;
    }

    // Kiểm tra sdt chi co số
    if (!/^\d+$/.test(phone) && !formatted) {
        input.classList.add('is-invalid');
        if (fromSelf)
            errorElement.textContent = 'Vui lòng chỉ nhập số cho mục này';
        if (!fromSelf && errorElement.textContent == "")
            errorElement.textContent = 'Vui lòng chỉ nhập số cho mục này';
        errorElement.style.display = 'block';
        input.value = "";
        return false;

    }

    // Kiểm tra độ dài sdt
    if ((phone.length < 9 || phone.length > 10) && !formatted) {
        input.classList.add('is-invalid');
        if (fromSelf)
            errorElement.textContent = 'Số điện thoại phải có từ 7 đến 8 số';
        if (!fromSelf && errorElement.textContent == "")
            errorElement.textContent = 'Số điện thoại phải có từ 7 đến 8 số';
        errorElement.style.display = 'block';
        input.value = "";
        return false;

    }

    input.classList.remove('is-invalid');
    errorElement.style.display = 'none';
    return true;
}

function validateCid(input, fromSelf = true) {
    var cid = input.value;
    var errorElement = document.getElementById('cid-error');

    // Kiểm tra cid trống
    if (cid == "") {
        input.classList.add('is-invalid');
        if (fromSelf)
            errorElement.textContent = 'Vui lòng nhập số CCCD';
        if (!fromSelf && errorElement.textContent == "")
            errorElement.textContent = 'Vui lòng nhập số CCCD';
        errorElement.style.display = 'block';
        input.value = "";
        return false;
    }

    // Kiểm tra cid chi co số
    if (!/^\d+$/.test(cid)) {
        input.classList.add('is-invalid');
        if (fromSelf)
            errorElement.textContent = 'Vui lòng chỉ nhập số cho mục này';
        if (!fromSelf && errorElement.textContent == "")
            errorElement.textContent = 'Vui lòng chỉ nhập số cho mục này';
        errorElement.style.display = 'block';
        input.value = "";
        return false;
    }

    input.classList.remove('is-invalid');
    errorElement.style.display = 'none';
    return true;
}

function formatPhoneNumber(input, fromSelf = true) {
    if (!validatePhone(input, fromSelf))
        return false;

    // Lấy giá trị nhập vào và loại bỏ các ký tự không phải số
    var phoneNumber = input.value.replace(/\D/g, '');

    // Phân vùng số điện thoại theo định dạng xxx-xxx-xxxx
    var formattedPhoneNumber = '';
    var part1 = phoneNumber.substring(0, 3);
    var part2 = phoneNumber.substring(3, 6);
    var part3 = phoneNumber.substring(6, 10);

    if (phoneNumber.length > 6) {
        formattedPhoneNumber = part1 + '-' + part2 + '-' + part3;
    } else if (phoneNumber.length > 3) {
        formattedPhoneNumber = part1 + '-' + part2;
    } else {
        formattedPhoneNumber = part1;
    }

    // Cập nhật giá trị của trường nhập (input)
    input.value = formattedPhoneNumber;
    formatted = true;
}

window.onload = () => {
    var dob = document.getElementById('dob');
    dob.setAttribute('max', new Date().toLocaleDateString('fr-ca'))

}

async function checkUsername(username) {
    console.log(222)
    try {
        const response = await fetch('/check_username', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({username: username})
        });

        // Kiểm tra mã phản hồi HTTP
        if (response.ok) {
            return true;
        } else {
            console.error('Đã xảy ra lỗi khi gửi yêu cầu đến API kiểm tra username.');
            return false;
        }
    } catch (error) {
        console.error('Đã xảy ra lỗi:', error);
    }
};
