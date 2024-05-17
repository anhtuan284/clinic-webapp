var countChart;
var revenueChart;
var percentChart; 

var medQuantityChart;
var medCountChart;

function reloadPageWithFilteredList(selectInput) {
    fetch(`/admin/thuocview/?danhmuc_id=${selectInput.value}`)
    .then(data => data.text())
    .then(html => {
        document.body.innerHTML = html
    })
    .catch(function (error) {
        console.log('request failed', error)
    });
}

function make_stats(monthInput) {
    get_revenue_percentage_by_month(monthInput);
    get_medicine_usage_stats_by_month(monthInput);
}

function get_revenue_percentage_by_month(monthInput) {
    fetch(`/api/revenue_percentage_stats/`, {
        method: 'POST',
        headers: {
            'content-type': 'application/json'
        },
        body: JSON.stringify({
            'month': monthInput.value
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Không thể thống kê được!!!');
        }
        return response.json();
    })
    .then(data => {
        // [
        //     //date_medicine_revenue_by_drug_assigned_prescription_list
        //     [
        //         {
        //             'prescription_date': row[0],
        //             'patient_count': row.patient_count,
        //             "total_date_medicine_revenue": row.total_date_medicine_revenue,
        //             "percentage": row.percentage
        //         },
        //         ...
        //     ],

        //     //date_revenue_by_drugless_prescription_list
        //     [
        //         {
        //             'prescription_date': row[0],
        //             'total_date_revenue': row.total_date_revenue,
        //             "percentage": row.percentage
        //         },
        //         ...
        //     ]    
        // ]

        date_medicine_revenue_by_drug_assigned_prescription_list = data[0];
        date_revenue_by_drugless_prescription_list = data[1];
        var revenueTable = document.getElementById("revenue-table");
        while (revenueTable.hasChildNodes())
            revenueTable.removeChild(revenueTable.childNodes[0])

        let labels = [];
        let dataCount = [];
        let dataRevenue = [];
        let dataPercent = [];

        //add data to table
        for (let i = 0; i < date_medicine_revenue_by_drug_assigned_prescription_list.length; i++)
        {

            var td_prescription_date = document.createElement("td");
            td_prescription_date.innerHTML = new Date(date_medicine_revenue_by_drug_assigned_prescription_list[i]["prescription_date"]).toDateString().toLocaleString("de-DE");
            labels.push(td_prescription_date.innerHTML);

            var td_patient_count = document.createElement("td");
            td_patient_count.innerHTML = date_medicine_revenue_by_drug_assigned_prescription_list[i]["patient_count"];
            dataCount.push(td_patient_count.innerHTML);

            var td_total_date_medicine_revenue = document.createElement("td");
            td_total_date_medicine_revenue.innerHTML = 
            parseFloat(date_medicine_revenue_by_drug_assigned_prescription_list[i]["total_date_medicine_revenue"]) + 
            parseFloat(date_revenue_by_drugless_prescription_list.find((obj) => {
                return obj['prescription_date'] === date_medicine_revenue_by_drug_assigned_prescription_list[i]['prescription_date']
            })['total_date_revenue']);
            dataRevenue.push(td_total_date_medicine_revenue.innerHTML);

            var td_percentage = document.createElement("td");
            td_percentage.innerHTML = 
            (parseFloat(date_medicine_revenue_by_drug_assigned_prescription_list[i]["percentage"]) + 
            parseFloat(date_revenue_by_drugless_prescription_list.find((obj) => {
                return obj['prescription_date'] === date_medicine_revenue_by_drug_assigned_prescription_list[i]['prescription_date']
            })['percentage'])).toFixed(2);
            dataPercent.push(td_percentage.innerHTML);

            var tr = document.createElement('tr');
            tr.appendChild(td_prescription_date);
            tr.appendChild(td_patient_count);
            tr.appendChild(td_total_date_medicine_revenue);
            tr.appendChild(td_percentage);
            revenueTable.appendChild(tr);
        }

        var table_thang = document.getElementById('table-thang');
        table_thang.innerHTML = '<strong>Tháng</strong>: ' + monthInput.value;

        var tr = document.createElement('tr');
        var td_total_revenue = document.createElement('td');
        td_total_revenue.setAttribute('colspan', '4')
        td_total_revenue.innerHTML = '0';
        for (let i = 0; i < revenueTable.rows.length; i++) {
            td_total_revenue.innerHTML = (parseFloat(td_total_revenue.innerHTML) + 
        parseFloat(revenueTable.rows[i].cells[2].innerHTML)).toString();
            
        }
        td_total_revenue.innerHTML = "<strong>Tổng Doanh Thu</strong>: " + td_total_revenue.innerHTML;
        tr.appendChild(td_total_revenue);
        revenueTable.appendChild(tr);

        countChartCtx = document.getElementById("countChart");
        if (countChart) countChart.destroy()

        countChart = drawBarChart(countChartCtx,
            labels=labels,
            data=[dataCount],
            legendLabel=['Số Bệnh Nhân'],
            title="Số Bệnh Nhân",
            tintColors=['green'],
            legendPos='right'
        );

        revenueChartCtx = document.getElementById("revenueChart");
        if (revenueChart) revenueChart.destroy();

        revenueChart = drawBarChart(revenueChartCtx,
            labels=labels,
            data=[dataRevenue],
            legendLabel=['Doanh Thu'],
            title="Doanh Thu",
            tintColors=['gold'],
            legendPos='right'
        );


        percentChartCtx = document.getElementById("percentChart");
        if (percentChart) percentChart.destroy();

        percentChart = drawDonutChart(percentChartCtx,
            labels=labels,
            data=dataPercent,
            legendLabel=['Tỉ Lệ'],
            title="Tỉ Lệ",
            tintColors=['red', 'blue', 'gold', 'green', 'diamond'],
            legendPos='right'
        );

    })
}

function get_medicine_usage_stats_by_month(monthInput) {
    fetch(`/api/medicine_usage_stats/`, {
        method: 'POST',
        headers: {
            'content-type': 'application/json'
        },
        body: JSON.stringify({
            'month': monthInput.value
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Không thể thống kê được!!!');
        }
        return response.json();
    })
    .then(data => {
        // [
        //     //medicine_stats
        //     [
        //         {
                    //     'medicine_id': row[0],
                    //     'medicine_name': row[1],
                    //     'unit_name': row[2],
                    //     'medicine_unit_quantity': row[3],
                    //     "quantity": row[4],
                    //     "use_count": row[5]
                    // }
        //         ...
        //     ],

        medicine_stats = data;
        var medicineTable = document.getElementById("medicine-table");
        while (medicineTable.hasChildNodes())
            medicineTable.removeChild(medicineTable.childNodes[0])

        labels = [];
        dataCount = [];
        var dataQuantity = [];

        console.log(medicine_stats);

        //add data to table
        for (let i = 0; i < medicine_stats.length; i++)
        {
            var td_medicine = document.createElement("td");
            td_medicine.innerHTML = medicine_stats[i]["medicine_name"];

            var td_unit = document.createElement("td");
            td_unit.innerHTML = medicine_stats[i]['medicine_unit_quantity'] + ' (viên, ml, gram) trên 1 ' + medicine_stats[i]["unit_name"];
            labels.push(td_medicine.innerHTML + '; ' +  td_unit.innerHTML);

            var td_quantity = document.createElement("td");
            td_quantity.innerHTML = medicine_stats[i]['quantity']
            dataQuantity.push(td_quantity.innerHTML);

            var td_use_count = document.createElement("td");
            td_use_count.innerHTML = medicine_stats[i]['use_count']
            dataCount.push(td_use_count.innerHTML);

            var tr = document.createElement('tr');
            tr.appendChild(td_medicine);
            tr.appendChild(td_unit);
            tr.appendChild(td_quantity);
            tr.appendChild(td_use_count);
            medicineTable.appendChild(tr);
        }

        var medicine_table_thang = document.getElementById('medicine-table-thang');
        medicine_table_thang.innerHTML = '<strong>Tháng</strong>: ' + monthInput.value;

        medQuantityChartCtx = document.getElementById("quantityChart");

        if (medQuantityChart) medQuantityChart.destroy()
            medQuantityChart = drawBarChart(medQuantityChartCtx,
                labels=labels,
                data=[dataQuantity],
                legendLabel=['Số Lượng Thuốc'],
                title="Số Lượng Thuốc",
                tintColors=['#5499C7'],
                legendPos='bottom'
            );

        medCountChartCtx = document.getElementById("medCountChart");

        if (medCountChart) medCountChart.destroy();

        medCountChart = drawBarChart(medCountChartCtx,
                labels=labels,
                data=[dataCount],
                legendLabel=['Số Lần Sử Dụng'],
                title="Số Lần Sử Dụng",
                tintColors=['#A569BD'],
            );

    })
}

function drawBarChart(ctx, labels, data, legendLabel, title, tintColors, legendPos) {

    let datasets = [];
    for (let i = 0; i < legendLabel.length; i++) {
        datasets.push({
            label: legendLabel[i],
            data: data[i],
            borderWidth: 1,
            backgroundColor: tintColors[i]
        });
    }

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            scales: {
                x: {
                    beginAtZero: true
                    },
                y: {
                    beginAtZero: true
                }
                
            },
            barThickness: 46,
            "plugins": {
                title: {
                    display: true,
                    text: title,
                    position: 'top'
                },
                "legend": {
                    display: true,
                    position: 'bottom'
                }
            },
            maintainAspectRatio: 'false'
        },
        
    });
}

function drawDonutChart(ctx, labels, data, legendLabel, title, tintColors, legendPos) {

    let datasets = [{
        data: data,
        backgroundColor: tintColors,
        hoverOffset: 4
    }];

    const chart_data = {
        labels: labels,
        datasets: datasets
    };

    return new Chart(ctx, {
        type: 'doughnut',
        data: chart_data,
        options: {
            "plugins": {
                "legend": {
                    position: legendPos
                },
                title: {
                    display: true,
                    text: title
                }
            },
            maintainAspectRatio: 'false'
        }
      });
}

