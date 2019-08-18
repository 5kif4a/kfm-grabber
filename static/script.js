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