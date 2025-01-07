function openPopup(taskId, taskText, taskDesc) {
    document.getElementById('popup').style.display = 'flex';
//    document.getElementById('task-id').value = taskId;
//    document.getElementById('task-text').value = taskText;
//    document.getElementById('update-form').action = `/edit/${task._Id}`;
}

function closePopup() {
    document.getElementById('popup').style.display = 'none';
}
