const projectInfoTable = document.getElementById('project-info-table');

const data = {put_answer_here};

function generateTable(data) {
  const tbody = projectInfoTable.querySelector('tbody');

  let lastCategory = null;
  let categoryRowspan = 0;

  data.forEach(item => {
    if (item.category !== lastCategory) {
      lastCategory = item.category;
      categoryRowspan = data.filter(i => i.category === item.category).length;
    } else {
      categoryRowspan = 0;
    }

    const tr = document.createElement('tr');

    if (categoryRowspan > 0) {
      const categoryCell = document.createElement('td');
      categoryCell.textContent = item.category;
      categoryCell.setAttribute('rowspan', categoryRowspan);
      tr.appendChild(categoryCell);
    }

    const taskCell = document.createElement('td');
    taskCell.textContent = item.task;
    tr.appendChild(taskCell);

    const reasonCell = document.createElement('td');
    reasonCell.textContent = item.reason;
    tr.appendChild(reasonCell);

    tbody.appendChild(tr);
  });
}

generateTable(data);
