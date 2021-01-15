const datasetTabBtn = document.getElementById('dataset-tab-btn');
const modelTabBtn = document.getElementById('model-tab-btn');

const datasetTabLi = document.getElementById('dataset-tab-li');
const modelTabLi = document.getElementById('model-tab-li');

const datasetTab = document.getElementById('dataset-tab');
const modelTab = document.getElementById('model-tab');

datasetTabBtn.onclick = e => {
    e.preventDefault();
    datasetTabLi.classList.add('is-active');
    modelTabLi.classList.remove('is-active');
    modelTab.classList.add('hidden');
    datasetTab.classList.remove('hidden');
}

modelTabBtn.onclick = e => {
    e.preventDefault();
    datasetTabLi.classList.remove('is-active');
    modelTabLi.classList.add('is-active');
    modelTab.classList.remove('hidden');
    datasetTab.classList.add('hidden');
}