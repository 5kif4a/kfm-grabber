function updateall(){
    if (confirm('Вы точно хотите обновить всю базу?')) {
        location.href = '/updateall';
    };
};

function toggle(source) {
  checkboxes = document.getElementsByName('select');
  for(var i=0, n=checkboxes.length;i<n;i++) {
    checkboxes[i].checked = source.checked;
  }
}

function addNewRow() {
    let table = document.getElementById("table");
    let row = table.insertRow(table.length);
    let column_count = document.getElementById('table').rows[0].cells.length;
    for(let i=0; i < column_count; i++){
        let ceil = row.insertCell(i);
        ceil.contentEditable = 'true';
    }
    row.cells[column_count-1].contentEditable = 'false';
    row.cells[column_count-1].innerHTML = '<button class="btn btn-outline-danger" onclick="deleteRow(this)"><i class="fas fa-backspace"></i></button>';
}

function deleteRow(r) {  // событие для удаления строки в таблице
    let i = r.parentNode.parentNode.rowIndex;
    document.getElementById("table").deleteRow(i);
}

var tableToObj = function( table ) {
    let trs = table.rows,
        trl = trs.length,
        i = 0,
        j = 0,
        keys = [],
        obj, ret = [];

    for (; i < trl; i++) {
        if (i == 0) {
            for (; j < trs[i].children.length; j++) {
                keys.push(trs[i].children[j].innerHTML);
            }
        } else {
            obj = {};
            for (j = 0; j < trs[i].children.length; j++) {
                obj[keys[j]] = trs[i].children[j].innerHTML;
            }
            delete obj['remove'];
            ret.push(obj);
        }
    }
    return ret;
};

function send_data() {
    let table = document.getElementById("table");
    let data = tableToObj(table);
    let t = window.location.pathname.split('/')[1];
    fetch('/'+ t +'/send', {
    method: "POST",
    credentials: "include",
    body: JSON.stringify(data),
    cache: "no-cache",
    redirect: 'follow',
    headers: new Headers({
      "content-type": "application/json"
    }),
  })
  .then(function(response) {
    if (response.status !== 200) {
      console.log(`Looks like there was a problem. Status code: ${response.status}`);
      return;
    }
    response.json().then(function(data) {
      console.log(data);
      window.location.href = '/' + t + '/page/1';
    });
  })
  .catch(function(error) {
    console.log("Fetch error: " + error);
});
}

function delete_rows() { // удалить из базы данных строки таблицы
    let table = document.getElementById('table');
    let checkboxes = table.getElementsByTagName('input');
    let idxs = [];
    for(let i=0; i < checkboxes.length; i++){
        if(checkboxes[i].checked){
            idxs.push(checkboxes[i].id);
        }
    }
    if(idxs.length > 0){
        if(confirm('Вы потверждаете удаление?')){
            let t = window.location.pathname.split('/')[1];
            fetch('/'+ t +'/delete', {
            method: "DELETE",
            credentials: "include",
            body: JSON.stringify(idxs),
            cache: "no-cache",
            redirect: 'follow',
            headers: new Headers({
              "content-type": "application/json"
            }),
          })
          .then(function(response) {
            if (response.status !== 200) {
              console.log(`Looks like there was a problem. Status code: ${response.status}`);
              return;
            }
            response.json().then(function(data) {
              console.log(data);
              window.location.href = '/' + t + '/page/1';
            });
          })
          .catch(function(error) {
            console.log("Fetch error: " + error);
        });
                }
    }
    else{
        alert('Вы не выбрали строки для удаления');
    }
}

