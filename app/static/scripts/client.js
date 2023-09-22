let testimonials;

const carouselContent = document.getElementById('carousel-content')
const corouselNavWrapper = document.getElementById('carousel-indicator-wrapper')

// load cleint json on initial load
async function loadTestimonials() {
    const req = await fetch('/static/data/testimonial.json')
    const res = await req.json()
    testimonials = res;

    // set all data in the section
    let carouselStr = '' , carouselIndicators = '';
    testimonials.forEach((element, index) => {
        carouselStr += `<div class="carousel-item ${index === 0 ? 'active' : ''}">
            <div class="content text-center" id="carousel-content">
                <div class="person"><img alt="" src="${element.image}"></div>
                    <h5>${element.name}</h5>
                    ${element?.app && '<h6>'+element.app+'</h6>'}
                    <h6>${element.designation}</h6>
                    <p>${element.comment}</p>
                </div>
        </div>`
        carouselIndicators += `
        <button aria-label="Slide ${index+1}" class="${index ===0 ? 'active' : ''}" data-bs-slide-to="${index}" data-bs-target="#carouselExampleIndicators" type="button"></button>
        `
    });
    carouselContent.innerHTML = carouselStr;
    corouselNavWrapper.innerHTML = carouselIndicators;

}

window.onload = loadTestimonials();
