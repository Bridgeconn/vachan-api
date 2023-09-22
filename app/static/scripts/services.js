// accordian section for services
const dynamicContentSection = document.getElementById('service-content')
const dynamicContentWrapper = document.getElementById('animatedDiv')

// service content data elements
const serviceHeader = document.getElementById('service-content-head')
const serviceBody = document.getElementById('service-content-body')

const contentBodyColors = [
    "rgba(153, 102 ,255,0.2)",
    "rgba(255, 179, 199,0.2)",
    "rgba(51, 221, 179, 0.2)",
    "rgba(158, 23, 145, 0.2)",
    "rgba(40, 193, 1, 0.2)",
    "rgba(0, 196, 196,0.2)"
]

let serviceContent;

// load service json on initial load
async function loadSeriveData() {
    const req = await fetch('/static/data/services.json')
    const res = await req.json()
    serviceContent = res;
}
window.onload = loadSeriveData();

const delay = ms => new Promise(res => setTimeout(res, ms));


async function setServiceContent(serviceName) {
    await loadSeriveData();
    const currentData = serviceContent[serviceName]
    if (currentData){
        serviceHeader.innerText = currentData.title;
        serviceBody.innerText = currentData.content;
    } else{
        // failed to get data
        serviceBody.innerText = 'something went wrong! Failed to load data';
    }
}

let lastClickedSection;

async function handleServiceClicked(serviceName) {
    const currentIndex = Object.keys(serviceContent).indexOf(serviceName);
    animatedDiv.style.backgroundColor = contentBodyColors[currentIndex];
    // accordian action
    if (animatedDiv.clientHeight === 0) {
        await setServiceContent(serviceName);
        animatedDiv.style.height = dynamicContentSection.scrollHeight + 'px';
        // dynamicContentWrapper.style.border = '1px solid #7c76BB';
        dynamicContentWrapper.scrollIntoView({behavior: 'smooth', block:'center'})
        
    } else {
        if (lastClickedSection === serviceName) {
            animatedDiv.style.height = '0';
            // await delay(450);
            // dynamicContentWrapper.style.border = 'none';
        } else {
            // load next content
            await setServiceContent(serviceName);
            animatedDiv.style.height = dynamicContentSection.scrollHeight + 'px';
            dynamicContentWrapper.scrollIntoView({behavior: 'smooth', block:'center'})
        }
    }

    // update last clicked section value
    lastClickedSection = serviceName;

}

const serviceCard = document.querySelectorAll('.serviceCard');

serviceCard.forEach(div => {
    div.addEventListener('click', function() {
      const name = this.getAttribute('name');
      handleServiceClicked(name)
    });
  });


