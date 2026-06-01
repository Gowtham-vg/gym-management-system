let menu = document.querySelector('#menu-icon');
let navbar = document.querySelector('.navbar');

menu.onclick = () => {
    menu.classList.toggle('bx-x');
    navbar.classList.toggle('active');
}


window.onscroll = () => {
    menu.classList.remove('bx-x');
    navbar.classList.remove('active');
}

const typed = new Typed('.multiple-text',  {
    strings: ['Physical Fitness', 'Weight Gain', 'Strength Training', 'Fat Lose', 'Weightlifting', 'Running'],
    typeSpeed: 60,
    backSpeed: 60,
    backDelay: 1000,
    loop: true,
 });

 //display dynamically
 document.addEventListener('DOMContentLoaded', function () {
    const categoryLinks = document.querySelectorAll('.category-link');
    const productContainer = document.querySelector('.product-container');

    categoryLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const category = this.getAttribute('data-category');

            // Fetch products from the server
            fetch(`/get_products_by_category?category=${category}`)
                .then(response => response.json())
                .then(products => {
                    productContainer.innerHTML = ''; // Clear current products

                    if (products.length === 0) {
                        productContainer.innerHTML = '<p>No products found for this category.</p>';
                        return;
                    }

                    // Add each product to the container
                    products.forEach(product => {
                        const productDiv = document.createElement('div');
                        productDiv.classList.add('product-card');
                        productDiv.innerHTML = `
                            <img src="/static/uploads/${product.image}" alt="${product.name}">
                            <h3>${product.name}</h3>
                            <p>Price: ₹${product.price}</p>
                        `;
                        productContainer.appendChild(productDiv);
                    });
                })
                .catch(error => console.error('Error fetching products:', error));
        });
    });
});


