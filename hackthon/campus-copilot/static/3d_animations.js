function initBackgroundScene() {
    const container = document.getElementById('background-scene');
    if (!container) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ alpha: true });

    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor(0x000000, 0);
    container.appendChild(renderer.domElement);

    const particlesGeometry = new THREE.BufferGeometry();
    const particlesCount = 1000;

    const posArray = new Float32Array(particlesCount * 3);
    for (let i = 0; i < particlesCount * 3; i++) {
        posArray[i] = (Math.random() - 0.5) * 5;
    }

    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));

    const particlesMaterial = new THREE.PointsMaterial({
        size: 0.005,
        color: 0x1E90FF,
        transparent: true,
        opacity: 0.8
    });

    const particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial);
    scene.add(particlesMesh);

    camera.position.z = 2;

    const animate = () => {
        requestAnimationFrame(animate);
        particlesMesh.rotation.x += 0.0003;
        particlesMesh.rotation.y += 0.0005;
        renderer.render(scene, camera);
    };

    animate();

    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
}

function apply3DCardEffect() {
    const cards = document.querySelectorAll('.card');

    cards.forEach(card => {
        card.addEventListener('mousemove', e => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = (y - centerY) / 10;
            const rotateY = (centerX - x) / 10;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
            card.style.transition = 'transform 0.1s';

            const shadowX = (x - centerX) / 20;
            const shadowY = (y - centerY) / 20;
            card.style.boxShadow = `${shadowX}px ${shadowY}px 20px rgba(0, 0, 0, 0.3)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
            card.style.transition = 'transform 0.5s, box-shadow 0.5s';
            card.style.boxShadow = '0px 5px 15px rgba(0, 0, 0, 0.1)';
        });
    });
}

function apply3DButtonEffect() {
    const buttons = document.querySelectorAll('.btn');

    buttons.forEach(button => {
        button.addEventListener('mouseenter', () => {
            button.style.transform = 'translateZ(10px)';
            button.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.2)';
        });

        button.addEventListener('mouseleave', () => {
            button.style.transform = 'translateZ(0)';
            button.style.boxShadow = '0 5px 10px rgba(0, 0, 0, 0.1)';
        });

        button.addEventListener('mousedown', () => {
            button.style.transform = 'translateZ(5px) scale(0.98)';
        });

        button.addEventListener('mouseup', () => {
            button.style.transform = 'translateZ(10px)';
        });
    });
}

function create3DLoadingSpinner() {
    const spinnerContainer = document.createElement('div');
    spinnerContainer.className = 'spinner-3d-container';
    spinnerContainer.style.display = 'none';

    const spinner = document.createElement('div');
    spinner.className = 'spinner-3d';

    for (let i = 0; i < 8; i++) {
        const face = document.createElement('div');
        face.className = 'spinner-face';
        spinner.appendChild(face);
    }

    spinnerContainer.appendChild(spinner);
    document.body.appendChild(spinnerContainer);

    $(document).ajaxStart(() => {
        spinnerContainer.style.display = 'flex';
    }).ajaxStop(() => {
        spinnerContainer.style.display = 'none';
    });
}

function applyParallaxEffect() {
    const parallaxElements = document.querySelectorAll('.parallax');

    window.addEventListener('mousemove', e => {
        const mouseX = e.clientX / window.innerWidth - 0.5;
        const mouseY = e.clientY / window.innerHeight - 0.5;

        parallaxElements.forEach(el => {
            const depth = parseFloat(el.getAttribute('data-depth')) || 0.1;
            const moveX = mouseX * depth * 100;
            const moveY = mouseY * depth * 100;

            el.style.transform = `translate3d(${moveX}px, ${moveY}px, 0)`;
        });
    });
}

function apply3DFlipEffect() {
    const flipCards = document.querySelectorAll('.event');

    flipCards.forEach(card => {
        if (!card.querySelector('.flip-front') && !card.querySelector('.flip-back')) {
            const content = card.innerHTML;
            card.innerHTML = '';

            const front = document.createElement('div');
            front.className = 'flip-front';
            front.innerHTML = content;

            const back = document.createElement('div');
            back.className = 'flip-back';
            back.innerHTML = `<p>Click to view details</p>`;

            card.appendChild(front);
            card.appendChild(back);
            card.classList.add('flip-card');
        }

        card.addEventListener('click', () => {
            card.classList.toggle('flipped');
        });
    });
}

function apply3DPageTransitions() {
    const links = document.querySelectorAll('a:not([target="_blank"])');

    links.forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.classList.contains('no-transition') || 
                this.getAttribute('data-no-transition')) {
                return;
            }

            const href = this.getAttribute('href');
            if (href.startsWith('#') || 
                href.startsWith('javascript:') || 
                href.startsWith('http')) {
                return;
            }

            e.preventDefault();
            document.body.classList.add('page-exit');
            setTimeout(() => {
                window.location.href = href;
            }, 500);
        });
    });

    document.addEventListener('DOMContentLoaded', () => {
        document.body.classList.add('page-enter');
    });
}

function toggleAnimations(enabled) {
    localStorage.setItem('animations_enabled', enabled);
    if (!enabled) {
        document.body.classList.add('animations-disabled');
    } else {
        document.body.classList.remove('animations-disabled');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const animationsEnabled = localStorage.getItem('animations_enabled') !== 'false';
    toggleAnimations(animationsEnabled);

    const animationToggle = document.getElementById('animation-toggle');
    if (animationToggle) {
        animationToggle.checked = animationsEnabled;
        animationToggle.addEventListener('change', function() {
            toggleAnimations(this.checked);
        });
    }

    if (animationsEnabled) {
        if (typeof THREE === 'undefined') {
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
            script.onload = function() {
                initBackgroundScene();
            };
            document.head.appendChild(script);
        } else {
            initBackgroundScene();
        }

        apply3DCardEffect();
        apply3DButtonEffect();
        create3DLoadingSpinner();
        applyParallaxEffect();
        apply3DFlipEffect();
        apply3DPageTransitions();
    }
});
