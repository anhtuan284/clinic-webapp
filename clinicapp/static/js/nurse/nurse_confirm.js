// window.onload = showTable()
//
// function showTable() {
//     // Lấy ngày mặc định từ hệ thống hoặc ngày hiện tại
//     var defaultDate = new Date().toISOString().split('T')[0]; // Lấy ngày hiện tại dưới dạng 'YYYY-MM-DD'
//
//     // Gửi yêu cầu GET với tham số date
//     fetch(`/nurse/approved_appointment?date=${defaultDate}`)
//         .then(response => response.json())
//         .then(data => {
//             // Xử lý dữ liệu sau khi nhận được
//             console.log(data); // Hiển thị dữ liệu trong console để kiểm tra
//         })
//         .catch(error => console.error('Error:', error));
// }


function showOverlay() {
    document.getElementById("overlay").style.display = "flex";
}

// Function to hide the overlay
function hideOverlay() {
    const overlay = document.querySelector('.overlay');
    const clonedCards = overlay.querySelectorAll('.card'); // Chọn tất cả các thẻ card trong overlay
    clonedCards.forEach(card => {
        card.remove(); // Xóa các thẻ card đã sao chép
    });
    document.getElementById("overlay").style.display = "none";
}

// Function to handle appointment confirmation

// function change_confirm(id, scheduled_date, scheduled_hour) {
//     fetch("/nurse/change_confirm", {
//         method: "post", body: JSON.stringify({
//             "id": id, "scheduled_date": scheduled_date, "scheduled_hour": scheduled_hour
//         }), headers: {
//             "Content-Type": "application/json"
//         }
//     })
//         .then(response => {
//             if (!response.ok) {
//                 showOverlay();
//                 const card = document.querySelector(`.card[data-id="${id}"]`);
//                 const listNoConfirm = card.closest('.list_no_confirm');
//                 const overlay = document.querySelector('.overlay');
//                 // Sao chép thẻ card để hiển thị trên overlay
//                 const clonedCard = card.cloneNode(true);
//                 clonedCard.querySelector('.confirm-appointment-btn').remove();
//
//                 overlay.appendChild(clonedCard);
//
//                 throw new Error('Failed to confirm appointment.');
//             }
//             // Tìm thẻ card được xác nhận bằng ID
//             const card = document.querySelector(`.card[data-id="${id}"]`);
//             if (!card) {
//                 throw new Error('Card not found.');
//             }
//             // Di chuyển thẻ từ list_no_confirm sang list_confirm
//             const listNoConfirm = card.closest('.list_no_confirm');
//             const listConfirm = document.querySelector('.list_confirm');
//             listConfirm.appendChild(card);
//             // Xóa nút "Xác nhận" khỏi card
//             card.querySelector('.confirm-appointment-btn').remove();
//         })
//         .catch(error => {
//             console.error('Error:', error);
//         });
// }
function change_confirm(id, scheduled_date, scheduled_hour) {
    fetch("/nurse/change_confirm", {
        method: "post", body: JSON.stringify({
            "id": id, "scheduled_date": scheduled_date, "scheduled_hour": scheduled_hour
        }), headers: {
            "Content-Type": "application/json"
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to confirm appointment.');
            }
            // Tìm thẻ card được xác nhận bằng ID
            const card = document.querySelector(`.card[data-appointment-id="${id}"]`);
            if (!card) {
                throw new Error('Card not found.');
            }
            // Di chuyển thẻ từ list_no_confirm sang list_confirm
            const listNoConfirm = card.closest('.list_no_confirm');
            const listConfirm = document.querySelector('.list_confirm');
            listConfirm.appendChild(card);
            // Xóa nút "Xác nhận" và "Từ chối" khỏi card
            card.querySelector('.confirm-appointment-btn').remove();
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function rejectAppointment(appointmentId, userId) {
    fetch("/api/update_appointment?appointment_id=" + appointmentId + "&user_id=" + userId + "&status=cancelled", {
        method: "PATCH", headers: {
            "Content-Type": "application/json"
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to reject appointment.');
            }
            // If successful, remove the card from the UI
            const card = document.querySelector(`.card[data-appointment-id="${appointmentId}"]`);
            if (card) {
                card.remove();
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function get_date_confirm() {
    // Trích xuất các ngày hẹn duy nhất
    var scheduledDates = [];
    var appointmentCards = document.querySelectorAll('.list_confirm .card');
    appointmentCards.forEach(function (card) {
        var scheduledDate = card.querySelector('.card-text:nth-child(3)').textContent.trim(); // Giả định thẻ <p> thứ ba chứa ngày hẹn
        if (!scheduledDates.includes(scheduledDate)) {
            scheduledDates.push(scheduledDate);
        }
    })
    return scheduledDates
}

var scheduledDates = get_date_confirm()

// function create_list_for_date() {
//     create_list_by_date()
//
// }

function create_list_by_date() {
    if (scheduledDates.length > 0) {
        fetch("/nurse/create_list_by_date", {
            method: "POST", headers: {
                "Content-Type": "application/json"
            }, body: JSON.stringify({scheduled_dates: scheduledDates})
        })
    }
}

// function card_data() {
//     var cardElements = document.querySelectorAll('.list_confirm .card');
//     var cardData = [];
//     cardElements.forEach(function (card) {
//         var appointmentId = card.dataset.appointmentId;
//         // var userId = card.dataset.userId; user_id: userId
//         cardData.push({appointment_id: appointmentId,});
//     });
//     return cardData
// }
function card_data() {
    var cardElements = document.querySelectorAll('.list_confirm .card');
    var cardData = [];
    cardElements.forEach(function (card) {
        var appointmentId = card.dataset.appointmentId; // Chú ý sử dụng dataset.appointmentId thay vì dataset.appointment_id
        var userId = card.dataset.userId;

        cardData.push({appointment_id: appointmentId, user_id: userId});

    });
    return cardData;
}


function create_list_for_date() {
    create_list_by_date()
    var cardData = card_data()

    // Gửi dữ liệu cardData đến server
    fetch('/api/update_appointment?status=approved', {
        method: 'PATCH', headers: {
            'Content-Type': 'application/json'
        }, body: JSON.stringify(cardData)
    }).then(function (response) {
        if (response.ok) {
            fetch('/nurse/send_list_email', {
                method: 'POST', headers: {
                    'Content-Type': 'application/json'
                }, body: JSON.stringify(cardData)
            })
            console.log('Card data sent successfully');
            location.reload();

        } else {
            console.error('Failed to send card data');
        }
    }).catch(function (error) {
        console.error('Error:', error);
    });
}