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


// async function setServiceContent(serviceName) {
//     await loadSeriveData();
//     const currentData = serviceContent[serviceName]
//     if (currentData){
//         serviceHeader.innerText = currentData.title;
//         serviceBody.innerText = currentData.content;
//     } else{
//         // failed to get data
//         serviceBody.innerText = 'something went wrong! Failed to load data';
//     }
// }

async function setServiceContent(serviceName) {
    await loadSeriveData();
    const currentData = serviceContent[serviceName];
    if (currentData) {
        serviceHeader.innerText = currentData.title;
        serviceBody.innerText = currentData.content;

        // Check if links exist in the JSON data
        if (currentData.links && currentData.links.length > 0) {
            const linkContainer = document.createElement('div');
            linkContainer.classList.add('service-link-container');

            // Iterate through the links and create anchor elements
            currentData.links.forEach((linkData, index) => {
                const linkElement = document.createElement('a');
                linkElement.href = linkData[`link${index + 1}`]; // Access link1, link2, etc.
                linkElement.target = "_blank"; // Opens link in a new tab
                linkElement.innerText = linkData[`linkname${index + 1}`] || 'Learn More'; // Use linkname or default text
                linkContainer.appendChild(linkElement);

                
                if (index < currentData.links.length - 1) {
                    const separator = document.createElement('span');
                    separator.innerText = ' | ';
                    linkContainer.appendChild(separator);
                }
            });

            linkContainer.style.marginTop = '10px'; // Adjust the value as needed


            // Append the link container to the service card's body
            serviceBody.appendChild(linkContainer);
        }
    } else {
        // failed to get data
        serviceBody.innerText = 'Something went wrong! Failed to load data.';
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


