let listMedicines = []
function add() {
    const quantity = document.getElementById('quantity');
    const usage = document.getElementById('usage');
    const unit = document.getElementById('selected-unit');
    const selectedMedicine = document.getElementById('selected-medicine');
    const medicine_id = selectedMedicine.value
    console.log("from add() func")

    if (selectedMedicine.value!=='' && quantity.value !== '' && usage.value !== '') {
        listMedicines.push({
            "medicine_name": selectedMedicine.options[selectedMedicine.selectedIndex].text,
            "medicine_id": medicine_id,
            "unit_text": unit.options[unit.selectedIndex].text,
            "unit_id": unit.value,
            "quantity": quantity.value,
            "usage": usage.value
        });

        // quantity.value = 1;
        // usage.value = '';
        // selectedMedicine.value=0;
        updateTable();
    }
    else {
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