// Define interfaces for type safety
interface Format {
  label: string;
  quality: string;
  url: string;
  ext: string;
}

interface VideoInfo {
  title: string;
  thumbnail: string;
  duration: string;
  formats: Format[];
}

// DOM Elements
const form = document.getElementById('download-form') as HTMLFormElement;
const urlInput = document.getElementById('tiktok-url') as HTMLInputElement;
const submitButton = form.querySelector('button[type="submit"]') as HTMLButtonElement;
const skeletonLoader = document.getElementById('skeleton-loader') as HTMLDivElement;
const videoInfoContainer = document.getElementById('video-info') as HTMLDivElement;
const errorMessage = document.getElementById('error-message') as HTMLDivElement;
const themeToggle = document.getElementById('theme-toggle') as HTMLButtonElement;
const themeIconLight = document.getElementById('theme-icon-light') as SVGElement;
const themeIconDark = document.getElementById('theme-icon-dark') as SVGElement;

// --- Theme Toggler ---
const applyTheme = (theme: 'dark' | 'light') => {
  if (theme === 'dark') {
    document.documentElement.classList.add('dark');
    themeIconLight.classList.remove('hidden');
    themeIconDark.classList.add('hidden');
  } else {
    document.documentElement.classList.remove('dark');
    themeIconLight.classList.add('hidden');
    themeIconDark.classList.remove('hidden');
  }
};

const toggleTheme = () => {
  const isDark = document.documentElement.classList.contains('dark');
  const newTheme = isDark ? 'light' : 'dark';
  localStorage.setItem('theme', newTheme);
  applyTheme(newTheme);
};

// Check for saved theme preference
const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'light') {
  applyTheme('light');
} else {
  applyTheme('dark'); // Default to dark
}

themeToggle.addEventListener('click', toggleTheme);

// --- Main Form Logic ---
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const url = urlInput.value.trim();
  if (!url) {
    showError('Please enter a TikTok URL.');
    return;
  }

  // UI state updates
  submitButton.disabled = true;
  submitButton.innerHTML = 'Fetching...';
  skeletonLoader.classList.remove('hidden');
  videoInfoContainer.classList.add('hidden');
  errorMessage.classList.add('hidden');

  try {
    const response = await fetch('/api/download', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url }),
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch video data.');
    }

    const data: VideoInfo = await response.json();
    displayVideoInfo(data);

  } catch (error) {
    console.error('Fetch error:', error);
    showError((error as Error).message || 'An unknown error occurred.');
  } finally {
    // Restore UI state
    submitButton.disabled = false;
    submitButton.innerHTML = 'Download';
    skeletonLoader.classList.add('hidden');
  }
});

const showError = (message: string) => {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
    videoInfoContainer.classList.add('hidden');
};

const displayVideoInfo = (data: VideoInfo) => {
  videoInfoContainer.innerHTML = `
    <div class="flex flex-col sm:flex-row gap-4 items-center">
        <img src="${data.thumbnail}" alt="Video thumbnail" class="w-32 h-32 object-cover rounded-lg shadow-md">
        <div class="text-center sm:text-left">
            <h2 class="text-lg font-semibold">${data.title}</h2>
            <p class="text-sm text-gray-500 dark:text-gray-400">Duration: ${data.duration}</p>
        </div>
    </div>
    <div class="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-2">
        ${data.formats.map(format => `
            <a href="${format.url}" download class="block w-full text-center bg-rose-500 text-white font-semibold py-2 px-4 rounded-md hover:bg-rose-600 transition-all transform hover:scale-105">
                Download ${format.label}
            </a>
        `).join('')}
    </div>
  `;
  videoInfoContainer.classList.remove('hidden');
};