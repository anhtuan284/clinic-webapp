function displayOfflinePayment() {
    document.getElementById("online_payment").style.display = "none";
    var content = document.getElementById("xuat-hoa-don");
    while (content.firstChild) {
        content.removeChild(content.lastChild);
    }

    //floating label tien nhan
    var divTienNhan = document.createElement("div");
    divTienNhan.setAttribute("class", "form-floating mb-3 mt-3");
    content.appendChild(divTienNhan);

    var inputTienNhan = document.createElement("input");
    var inputTotal = document.getElementById('total')
    inputTienNhan.setAttribute("type", "number");
    inputTienNhan.setAttribute("class", "form-control");
    inputTienNhan.setAttribute("id", "tien_nhan");
    inputTienNhan.setAttribute("required", "True");
    inputTienNhan.setAttribute("min", inputTotal.value);
    inputTienNhan.setAttribute("placeholder", "Nhập tiền nhận");
    inputTienNhan.setAttribute("name", "tien_nhan");
    inputTienNhan.addEventListener("input", () => {
        var total = document.getElementById("total");
        var inputTienThoi = document.getElementById("tien_thoi");
        inputTienNhan.setAttribute("value", inputTienNhan.value);
        inputTienThoi.setAttribute("value", (inputTienNhan.value - total.value));
    });
    divTienNhan.appendChild(inputTienNhan);

    var labelTienNhan = document.createElement("label");
    labelTienNhan.setAttribute("for", "tien_nhan");
    labelTienNhan.innerHTML = "Tiền Nhận"
    divTienNhan.appendChild(labelTienNhan);

    //floating label tien thoi
    var divTienThoi = document.createElement("div");
    divTienThoi.setAttribute("class", "form-floating mb-3 mt-3");
    content.appendChild(divTienThoi);

    var inputTienThoi = document.createElement("input");
    inputTienThoi.setAttribute("type", "number");
    inputTienThoi.setAttribute("class", "form-control");
    inputTienThoi.setAttribute("id", "tien_thoi");
    inputTienThoi.setAttribute("placeholder", "Nhập tiền thối");
    inputTienThoi.setAttribute("name", "tien_thoi");
    inputTienThoi.setAttribute("readonly", "true");
    divTienThoi.appendChild(inputTienThoi);

    var labelTienThoi = document.createElement("label");
    labelTienThoi.setAttribute("for", "tien_thoi");
    labelTienThoi.innerHTML = "Tiền Thối"
    divTienThoi.appendChild(labelTienThoi);

    //button xac nhan thanh toan
    //<button type="button" class="btn btn-outline-danger">Danger</button>
    var divXacNhan = document.createElement("div");
    divXacNhan.setAttribute("class", "form-floating mb-3 mt-3 d-flex flex-row-reverse");
    content.appendChild(divXacNhan);

    var buttonXacNhan = document.createElement("input");
    buttonXacNhan.setAttribute("type", "submit");
    buttonXacNhan.setAttribute("class", "btn btn-outline-danger");
    buttonXacNhan.setAttribute("value", "Xác nhận hoá đơn");
    divXacNhan.appendChild(buttonXacNhan);
}

function displayOnlinePayment() {
    var content = document.getElementById("xuat-hoa-don");
    while (content.firstChild) {
        content.removeChild(content.lastChild);
    }
    document.getElementById("online_payment").style.display = "block";

    //xu ly giao dien online payment va goi api online payment o day
    //dung content de xu ly giao dien
}




