let listMedicines = []

function add() {
    const selectedMedicine = document.getElementById('selected-medicine');

    const quantity = document.getElementById('quantity');
    const usage = document.getElementById('usage');
    const unit = document.getElementById('selected-unit');
    const medicine_id = selectedMedicine.value

    if (selectedMedicine.value !== '' && quantity.value !== '' && usage.value !== '') {
        const existingMedicine = listMedicines.find(medicine => medicine.medicine_id === medicine_id);
        if (quantity.value <= 50) {
            if (!existingMedicine) {
                listMedicines.push({
                    "medicine_name": selectedMedicine.options[selectedMedicine.selectedIndex].text,
                    "medicine_id": medicine_id,
                    "unit_text": unit.options[unit.selectedIndex].text,
                    "unit_id": unit.value,
                    "quantity": quantity.value,
                    "usage": usage.value
                });
            } else {
                alert("Thuốc đã tồn tại trong phiếu")
            }
            quantity.value = 1;
            usage.value = '';
            selectedMedicine.value = 0;
            unit.value = 1;
            updateTable();
        } else {
            alert("Số lượng thuốc không hợp lệ");
        }
    } else {
        alert("Chưa nhập đủ thông tin thuốc")
    }
}

function updateTable() {
    const tableBody = document.getElementById('table-medicines');
    tableBody.innerHTML = '';
    for (let i = 0; i < listMedicines.length; i++) {
        const row = document.createElement('tr');
        row.innerHTML = `
                            <td>${i + 1}</td>
                            <td style="width: 400px;">
                                <input name="list-medicine_id" hidden value="${listMedicines[i].medicine_id}" />
                                <div style="width:100%;">${listMedicines[i].medicine_name}<div/>
                            </td>
                            <td>
                                <input name="list-unit" hidden value="${listMedicines[i].unit_id}"/>
                                <div style="width:100%;">${listMedicines[i].unit_text}<div/>
                            </td>
                            <td>
                                <input class="border-0" style="outline: none; width:100%;" name="list-quantity" value="${listMedicines[i].quantity}"/>
                            </td>
                            <td>
                                <input class="border-0" style="outline: none; width:100%;" name="list-usage" value="${listMedicines[i].usage}"/>
                            </td>
                            <td>
                                <div class="m-auto"><input type="button" class="btn btn-danger py-1" onclick="deleteRow(this)" value="Xóa"/></div>
                            </td>

        `;
        tableBody.appendChild(row);
    }
}

function deleteRow(index) {
    if (confirm("Bạn có muốn xóa thuốc vừa chọn?") === true)
        listMedicines.splice(index, 1);
    updateTable();
}

function cancelCreatePres() {
    if (confirm("Hủy phiếu khám này?") === true) {
        window.location.href = "/"
    }
}


function fetchPatientInfo() {
    const patientId = document.getElementById('patient_cid').value;
    console.info(2222)
    fetch(`/api/patient/${patientId}`)
        .then(response => response.json())
        .then(data => {
            if (data) {
                console.log(data)
                document.getElementById('patient-name').value = data.name;
                document.getElementById('patient_id').value = data.id;
            } else {
                alert("Không tìm thấy bệnh nhân với CID này.");
                document.getElementById('patient-name').value = "";
            }
        })
        .catch(error => console.error('Error:', error));

}


function fetchMedicinesByCategory(categoryId) {
    fetch(`/api/medicines/category/${categoryId}`)
        .then(response => response.json())
        .then(data => {
            const medicineSelect = document.getElementById('selected-medicine');
            // remove old options
            while (medicineSelect.firstChild) {
                medicineSelect.removeChild(medicineSelect.firstChild);
            }
            // add new options
            data.forEach(medicine => {
                const option = document.createElement('option');
                option.value = medicine.id;
                option.textContent = medicine.name;
                medicineSelect.appendChild(option);
            });
        })
        .catch(error => console.error('Error:', error));
}
