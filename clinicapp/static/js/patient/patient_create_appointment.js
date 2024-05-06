window.onload = checkAppointmentDate; // Gọi hàm kiểm tra ngay khi trang được tải lần đầu

var today = new Date().toISOString().split('T')[0];
// document.getElementById("datepicker").value = today;

// Thiết lập giá trị min cho input date
document.getElementById("datepicker").setAttribute("min", today);

// Kiểm tra nếu ngày là quá khứ thì disable input
document.getElementById("datepicker").addEventListener("change", function () {
    var selectedDate = new Date(this.value);
    var currentDate = new Date();
    if (selectedDate < currentDate) {
        this.disabled = true;
    } else {
        this.disabled = false;
    }
});

function resetData() {
    // Ẩn thông báo không khả dụng và cửa sổ chọn giờ
    document.getElementById("unavailableMessage").style.display = "none";
    document.getElementById("class-timepicker").style.display = "none";
    document.getElementById("gateway").style.display = "none";

    // Xóa tất cả các tùy chọn trong select box
    document.getElementById("timepicker").innerHTML = '';
    document.getElementById("bookAppointmentButton").style.display = "none";
    document.getElementById("payAndBookAppointmentButton").style.display = "none";


    // Reset các radio button về trạng thái mặc định
    document.querySelectorAll('input[name="payment_method"]').forEach(function (radio) {
        radio.checked = false;
    });
}

// Hàm kiểm tra ngày hẹn khi trang được tải lần đầu
function checkAppointmentDate() {
    var selectedDate = document.getElementById("datepicker").value;
    if (!selectedDate) {
        // Không có ngày nào được chọn
        return;
    }
    // Gửi yêu cầu kiểm tra ngày thông qua fetch
    fetch(`/check-appointment-date?date=${selectedDate}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'available') {
                document.getElementById("paymentMethodSection").style.display = "block";
                document.getElementById("unavailableMessage").style.display = "none";
                document.getElementById("datepicker").disabled = false;
            } else {
                document.getElementById("paymentMethodSection").style.display = "none";
                document.getElementById("unavailableMessage").style.display = "block";
                document.getElementById("datepicker").addEventListener("change", function () {
                    this.disabled = false;
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Hàm xử lý sự kiện khi thay đổi phương thức thanh toán
function handlePaymentMethodChange() {
    var selectedPaymentMethod = document.querySelector('input[name="payment_method"]:checked').value;
    var selectedDate = document.getElementById("datepicker").value;

    if (selectedPaymentMethod === 'direct') {
        // Gọi route khi chọn thanh toán trực tuyến
        fetch(`/get-scheduled-hour-confirm?date=${selectedDate}`)
            .then(response => response.json())
            .then(data => {
                var unavailableHoursString = JSON.stringify(data);
                console.log(unavailableHoursString);
                document.getElementById("class-timepicker").style.display = "block";
                document.getElementById("timepicker").innerHTML = '';
                document.getElementById("bookAppointmentButton").style.display = "none";
                document.getElementById("payAndBookAppointmentButton").style.display = "block";
                document.getElementById("gateway").style.display = "block";
                  document.querySelectorAll('input[name="way"]').forEach(function (radio) {
        radio.checked = false;
    });

                initializeTimeOptions(unavailableHoursString);
            })
            .catch(error => {
                console.error('Error:', error);
            });
    } else if (selectedPaymentMethod === 'clinic') {
        // Gọi route khi chọn thanh toán tại quầy
        fetch(`/get-scheduled-hour-no-confirm?date=${selectedDate}`)
            .then(response => response.json())
            .then(data => {
                var unavailableHoursString = JSON.stringify(data);
                console.log(unavailableHoursString);
                document.getElementById("class-timepicker").style.display = "block";
                document.getElementById("bookAppointmentButton").style.display = "block";
                document.getElementById("timepicker").innerHTML = '';
                document.getElementById("payAndBookAppointmentButton").style.display = "none";
                document.getElementById("gateway").style.display = "none";

                initializeTimeOptions(unavailableHoursString);
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }
}

// Lắng nghe sự kiện onchange của input ngày (datepicker)
document.getElementById("datepicker").addEventListener("change", function () {
    resetData(); // Reset dữ liệu khi chọn ngày mới
    checkAppointmentDate(); // Kiểm tra ngày hẹn mới
});

// Lắng nghe sự kiện onchange của radio button phương thức thanh toán
document.querySelectorAll('input[name="payment_method"]').forEach(function (radio) {
    radio.addEventListener('change', handlePaymentMethodChange);
});

// Hàm khởi tạo các tùy chọn thời gian dựa trên dữ liệu từ fetch
function initializeTimeOptions(unavailableHoursString) {
    var startTime = 7 * 60; // 7:00 AM tính bằng phút
    var endTime = 21 * 60; // 9:00 PM tính bằng phút
    var interval = 15; // Khoảng thời gian giữa mỗi tùy chọn, tính bằng phút

    // Parse unavailableHoursString thành một mảng JavaScript
    var unavailableHours = JSON.parse(unavailableHoursString);

    // Tạo một mảng chứa tất cả các giờ bắt đầu không bị ảnh hưởng bởi unavailableHours
    var availableStartTimes = [];

    // Duyệt qua các giờ bắt đầu và lọc ra các giờ khả dụng
    for (var i = startTime; i < endTime; i += interval) {
        var hour = Math.floor(i / 60);
        var minute = i % 60;

        var formattedHour = hour < 10 ? '0' + hour : hour;
        var formattedMinute = minute < 10 ? '0' + minute : minute;

        var startTimeFormatted = formattedHour + ':' + formattedMinute;

        // Nếu giờ bắt đầu không tồn tại trong unavailableHours, thêm vào mảng availableStartTimes
        if (!unavailableHours.includes(startTimeFormatted)) {
            var endTimeMinutes = i + interval;
            var endHour = Math.floor(endTimeMinutes / 60);
            var endMinute = endTimeMinutes % 60;

            var formattedEndHour = endHour < 10 ? '0' + endHour : endHour;
            var formattedEndMinute = endMinute < 10 ? '0' + endMinute : endMinute;

            var endTimeFormatted = formattedEndHour + ':' + formattedEndMinute;

            availableStartTimes.push({value: i, text: startTimeFormatted + ' - ' + endTimeFormatted});
        }
    }

    // Xóa các tùy chọn hiện có và thêm các tùy chọn mới vào select box
    $('#timepicker').empty().append(availableStartTimes.map(option => $('<option>', option)));
}