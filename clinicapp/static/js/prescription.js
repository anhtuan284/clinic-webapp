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
                            <td class="align-middle">${i + 1}</td>
                            <td class="align-middle" style="width: 400px;">
                                <input name="list-medicine_id" hidden value="${listMedicines[i].medicine_id}" />
                                <div style="width:100%;">${listMedicines[i].medicine_name}<div/>
                            </td>
                            <td class="align-middle">
                                <input name="list-unit" hidden value="${listMedicines[i].unit_id}"/>
                                <div style="width:100%;">${listMedicines[i].unit_text}<div/>
                            </td>
                            <td class="align-middle">
                                <input class="border-0" name="list-quantity" hidden value="${listMedicines[i].quantity}"/>
                                <span>${listMedicines[i].quantity}<span/>
                            </td>
                            <td class="align-middle col-5">
                                <input class="border-0" name="list-usage" hidden value="${listMedicines[i].usage}"/>
                                <span>${listMedicines[i].usage}<span/>
                            </td>
                            <td class="align-middle">
                                <div class="m-auto"><input type="button" class="btn btn-danger py-1 btn-sm" onclick="deleteRow(this)" value="Xóa"/></div>
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
    const patientCid = document.getElementById('patient_cid').value;
    const scheduled_date = document.getElementById('scheduled_date').value;
    console.log(scheduled_date)
    fetch(`/api/patient/${patientCid}`, {
        method: 'POST',
        headers: {
            'content-type': 'application/json'
        },
        body: JSON.stringify({
            scheduled_date: scheduled_date
        })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Không thể tìm thấy bệnh nhân');
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('patient-name').value = data.name;
            document.getElementById('patient_id').value = data.id;
            document.getElementById('appointment_id').value = data.appointment_id;
        })
        .catch(error => {
            alert(error.message);
            document.getElementById('patient-name').value = "";
        });
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
            fetchMedicineUnits(data[0].id)
            data.forEach(medicine => {
                const option = document.createElement('option');
                option.value = medicine.id;
                option.textContent = medicine.name;
                medicineSelect.appendChild(option);
            });
        })
        .catch(error => console.error('Error:', error));
}

function fetchMedicineUnits(medicineId) {
    fetch(`/api/medicines/units/${medicineId}`)
        .then(response => response.json())
        .then(data => {
            const unitSelected = document.getElementById('selected-unit');
            // remove old options
            while (unitSelected.firstChild) {
                unitSelected.removeChild(unitSelected.firstChild);
            }

            data.forEach(medicine_unit => {
                const option = document.createElement('option');
                option.value = medicine_unit.id;
                option.textContent = medicine_unit.name;
                unitSelected.appendChild(option);
            });
        })
        .catch(error => console.error('Error:', error));
}


function viewPatientHistory() {
    const patientId = document.getElementById('patient_id').value;
    console.log(patientId)
    if (!patientId || patientId === '' || typeof patientId === undefined || patientId === null || patientId === '0') {
        alert("Không tìm thấy bệnh nhân này !");
    } else {
        window.location.href = `/patient/${patientId}/history`;
    }
}
