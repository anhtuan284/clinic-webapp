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
document.getElementById("datepicker").addEventListener("change", function () {
    resetData(); // Reset dữ liệu khi chọn ngày mới
    checkAppointmentDate(); // Kiểm tra ngày hẹn mới
});


function resetData() {
    document.getElementById("unavailableMessage").style.display = "none";
    document.getElementById("class-timepicker").style.display = "none";
    document.getElementById("timepicker").innerHTML = '';
    document.getElementById("bookAppointmentButton").style.display = "none";
    document.getElementById("payAndBookAppointmentButton").style.display = "none";
}

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
                document.getElementById("unavailableMessage").style.display = "none";
                document.getElementById("datepicker").disabled = false;
                fetch(`/get-scheduled-hour-confirm?date=${selectedDate}`)
                    .then(response => response.json())
                    .then(data => {
                        var unavailableHoursString = JSON.stringify(data);
                        console.log(unavailableHoursString);
                        document.getElementById("class-timepicker").style.display = "block";
                        document.getElementById("timepicker").innerHTML = '';
                        document.getElementById("bookAppointmentButton").style.display = "block";
                        initializeTimeOptions(unavailableHoursString, selectedDate);
                    })
                    .catch(error => {
                        console.error('Error:', error);
                    });
            } else {
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

function initializeTimeOptions(unavailableHoursString, dateInput) {
    var currentDate = new Date();
    var currentDay = currentDate.getDate();
    var currentMonth = currentDate.getMonth() + 1;
    var currentYear = currentDate.getFullYear();

    // Format ngày hiện tại
    var formattedCurrentDate = currentYear + '-' + (currentMonth < 10 ? '0' : '') + currentMonth + '-' + (currentDay < 10 ? '0' : '') + currentDay;

    // Lấy giờ hiện tại
    var currentHour = currentDate.getHours();
    var currentMinute = currentDate.getMinutes();

    // Kiểm tra nếu ngày đã chọn khác ngày hiện tại
    if (dateInput === formattedCurrentDate) {
        // Ngày đã chọn là ngày hiện tại, lấy giờ hiện tại
        var startTime = currentHour + ':' + (currentMinute < 10 ? '0' : '') + currentMinute;
        // Gán giờ bắt đầu vào thẻ input giờ
        document.getElementById('timepicker').value = startTime;

        // Thêm các giờ trước giờ hiện tại vào mảng unavailableHours
        var currentHourMinutes = currentHour * 60 + currentMinute;
        var unavailableHours = JSON.parse(unavailableHoursString);
        for (var i = 0; i < currentHourMinutes; i += 15) {
            var hour = Math.floor(i / 60);
            var minute = i % 60;
            var formattedHour = hour < 10 ? '0' + hour : hour;
            var formattedMinute = minute < 10 ? '0' + minute : minute;
            var startTimeFormatted = formattedHour + ':' + formattedMinute;
            unavailableHours.push(startTimeFormatted);
        }
        // Cập nhật unavailableHoursString
        unavailableHoursString = JSON.stringify(unavailableHours);
    }

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
