var countChart;
var revenueChart;
var percentChart; 

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

        countChartCtx = document.getElementById("countChart");
        revenueChartCtx = document.getElementById("revenueChart");
        percentChartCtx = document.getElementById("percentChart");

        if (countChart) countChart.destroy()
        if (revenueChart) revenueChart.destroy()
        if (percentChart) percentChart.destroy()

        countChart = drawChart(countChartCtx, labels=labels, data=dataCount, "Số Bệnh Nhân", type="bar", legendPos='right');
        revenueChart = drawChart(revenueChartCtx, labels=labels, data=dataRevenue, "Doanh Thu", type="bar", legendPos='right');
        percentChart = drawChart(percentChartCtx, labels=labels, data=dataPercent, "Tỉ Lệ", type="pie", radius = "50%");

    })

}

function drawChart(ctx, labels, data, title, type, radius, legendPos) {
    return new Chart(ctx, {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                    label: labels,
                    data: data,
                    borderWidth: 1,
                    backgroundColor: ['red', 'green', 'blue', 'gold', 'brown'],
                    radius: radius,
                }],
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
                        position: 'bottom'
                    },
                    "legend": {
                        display: true,
                        position: 'right'
                    }
                },
            },

    });
}