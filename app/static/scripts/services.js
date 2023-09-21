// accordian section for services
const dynamicContentSection = document.getElementById('service-content')
const dynamicContentWrapper = document.getElementById('animatedDiv')

// service content data elements
const serviceHeader = document.getElementById('service-content-head')
const serviceBody = document.getElementById('service-content-body')


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
    console.log({currentData});
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
    console.log({serviceName, serviceContent});
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

const servicesBtn = document.querySelectorAll('.service-icon-btn');

servicesBtn.forEach(div => {
    div.addEventListener('click', function() {
      const name = this.getAttribute('name');
      handleServiceClicked(name)
    });
  });


