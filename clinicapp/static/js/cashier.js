function displayOfflinePayment() {
    var content = document.getElementById("xuat-hoa-don");
    var divTienNhan = document.createElement("div");
    divTienNhan.setAttribute("class", "form-floating mb-3 mt-3");
    content.appendChild(divTienNhan);
    var labelTienNhan = document.createElement("input");
    labelTienNhan.setAttribute("type", "text");
    labelTienNhan.setAttribute("class", "form-control");
    labelTienNhan.setAttribute("id", "tien_nhan");
    labelTienNhan.setAttribute("placeholder", "Nhập tiền nhận");
    labelTienNhan.setAttribute("name", "tien_nhan");
    divTienNhan.appendChild(labelTienNhan);

}