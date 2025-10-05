// ML-powered dashboard functionality
class MLDashboard {
    constructor() {
        this.apiEndpoints = {
            // dashboard URLs are mounted under /dashboard/ (see project's urls.py)
            predictions: '/dashboard/api/ml/predictions/',
            anomalies: '/dashboard/api/ml/anomalies/',
            scenarios: '/dashboard/api/ml/scenarios/',
            health: '/dashboard/api/ml/health-recommendations/',
            chat: '/dashboard/api/ml/chat/'
        };
        this.updateInterval = 300000; // 5 minutes
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.startRealTimeUpdates();
        this.initializeMLComponents();
    }

    setupEventListeners() {
        // Scenario simulation buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-scenario]')) {
                this.runScenario(e.target.dataset.scenario);
            }
        });

        // Health chat
        const chatInput = document.getElementById('health-chat-input');
        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendChatMessage(e.target.value);
                }
            });
        }
    }

    async fetchMLPredictions(location) {
        try {
            const response = await fetch(`${this.apiEndpoints.predictions}?location=${location}`);
            const data = await response.json();
            this.updatePredictionDisplay(data);
            return data;
        } catch (error) {
            console.error('Failed to fetch ML predictions:', error);
            return null;
        }
    }

    async checkAnomalies(location) {
        try {
            const response = await fetch(`${this.apiEndpoints.anomalies}?location=${location}`);
            const data = await response.json();
            if (data.anomaly_detected) {
                this.showAnomalyAlert(data);
            }
            return data;
        } catch (error) {
            console.error('Failed to check anomalies:', error);
            return null;
        }
    }

    async runScenario(scenarioType) {
        const button = document.querySelector(`[data-scenario="${scenarioType}"]`);
        if (button) {
            button.innerHTML = '<i class="fas fa-spinner animate-spin mr-1"></i>Running...';
            button.disabled = true;
        }

        try {
            const response = await fetch(this.apiEndpoints.scenarios, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    scenario: scenarioType,
                    location: this.getCurrentLocation()
                })
            });

            const data = await response.json();
            this.displayScenarioResults(data);
        } catch (error) {
            console.error('Scenario simulation failed:', error);
            EcoSky.showError('Failed to run scenario simulation');
        } finally {
            if (button) {
                button.innerHTML = button.dataset.originalText || 'Run Scenario';
                button.disabled = false;
            }
        }
    }

    async sendChatMessage(message) {
        if (!message.trim()) return;

        const chatContainer = document.getElementById('health-chat-messages');
        if (!chatContainer) return;

        // Add user message
        this.addChatMessage(message, 'user');

        // Clear input
        document.getElementById('health-chat-input').value = '';

        try {
            const response = await fetch(this.apiEndpoints.chat, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    message: message,
                    location: this.getCurrentLocation(),
                    current_aqi: this.getCurrentAQI()
                })
            });

            const data = await response.json();
            this.addChatMessage(data.response, 'bot');
        } catch (error) {
            console.error('Chat request failed:', error);
            this.addChatMessage('Sorry, I encountered an error. Please try again.', 'bot');
        }
    }

    addChatMessage(message, sender) {
        const chatContainer = document.getElementById('health-chat-messages');
        if (!chatContainer) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `flex ${sender === 'user' ? 'justify-end' : 'justify-start'} mb-3`;
        
        messageDiv.innerHTML = `
            <div class="max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                sender === 'user' 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-200 text-gray-800'
            }">
                ${sender === 'bot' ? '<i class="fas fa-robot mr-2"></i>' : ''}
                ${message}
            </div>
        `;

        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    updatePredictionDisplay(data) {
        if (!data || !data.hourly_forecast) return;

        // Update prediction chart
        const chart = Chart.getChart('prediction-chart');
        if (chart && data.hourly_forecast) {
            const labels = data.hourly_forecast.map((_, i) => `${i * 3}h`);
            const values = data.hourly_forecast.map(f => f.predicted_aqi);
            
            chart.data.labels = labels;
            chart.data.datasets[0].data = values;
            chart.update();
        }

        // Update prediction text
        const predictions = data.hourly_forecast;
        if (predictions.length >= 3) {
            this.updatePredictionText('6h', predictions[2].predicted_aqi);
            this.updatePredictionText('12h', predictions[4]?.predicted_aqi || predictions[predictions.length-1].predicted_aqi);
            this.updatePredictionText('24h', predictions[predictions.length-1].predicted_aqi);
        }
    }

    updatePredictionText(timeframe, aqi) {
        const element = document.querySelector(`[data-prediction="${timeframe}"]`);
        if (element) {
            const category = EcoSky.getAQICategory(aqi);
            const color = EcoSky.getAQIColor(aqi);
            element.innerHTML = `<span class="font-semibold" style="color: ${color}">${category} (${aqi} AQI)</span>`;
        }
    }

    showAnomalyAlert(data) {
        const alertHtml = `
            <div class="fixed top-20 right-4 z-50 max-w-sm bg-red-50 border border-red-200 rounded-lg shadow-lg p-4 animate-bounce-in">
                <div class="flex items-start">
                    <i class="fas fa-exclamation-triangle text-red-600 mr-2 mt-1"></i>
                    <div>
                        <h4 class="font-semibold text-red-800">Anomaly Detected</h4>
                        <p class="text-sm text-red-700 mt-1">${data.message}</p>
                        <div class="mt-2">
                            <button onclick="this.parentElement.parentElement.parentElement.remove()" 
                                    class="text-xs text-red-600 hover:text-red-800">Dismiss</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', alertHtml);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            const alert = document.querySelector('.animate-bounce-in');
            if (alert) alert.remove();
        }, 10000);
    }

    displayScenarioResults(data) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-96 overflow-y-auto">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-xl font-semibold">Scenario Results</h3>
                    <button onclick="this.closest('.fixed').remove()" class="text-gray-500 hover:text-gray-700">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="space-y-4">
                    ${Object.entries(data).map(([scenario, result]) => `
                        <div class="border rounded-lg p-4">
                            <h4 class="font-medium mb-2">${scenario.replace('_', ' ').toUpperCase()}</h4>
                            <div class="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                    <span class="text-gray-600">Avg Change:</span>
                                    <span class="font-semibold ${result.avg_change > 0 ? 'text-red-600' : 'text-green-600'}">
                                        ${result.avg_change > 0 ? '+' : ''}${result.avg_change.toFixed(1)} AQI
                                    </span>
                                </div>
                                <div>
                                    <span class="text-gray-600">Max AQI:</span>
                                    <span class="font-semibold" style="color: ${EcoSky.getAQIColor(result.max_aqi)}">
                                        ${result.max_aqi}
                                    </span>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    initializeMLComponents() {
        // Initialize health chat if present
        const chatContainer = document.getElementById('health-chat-container');
        if (chatContainer) {
            this.initializeHealthChat();
        }

        // Initialize scenario buttons
        document.querySelectorAll('[data-scenario]').forEach(button => {
            button.dataset.originalText = button.innerHTML;
        });

        // Load initial ML data
        this.loadInitialMLData();
    }

    initializeHealthChat() {
        const chatHtml = `
            <div class="bg-white rounded-lg shadow-lg p-4 max-w-md">
                <div class="flex items-center justify-between mb-3">
                    <h4 class="font-semibold text-gray-800">Health Assistant</h4>
                    <i class="fas fa-robot text-blue-500"></i>
                </div>
                <div id="health-chat-messages" class="h-48 overflow-y-auto mb-3 space-y-2">
                    <div class="flex justify-start">
                        <div class="bg-gray-200 text-gray-800 px-3 py-2 rounded-lg max-w-xs">
                            <i class="fas fa-robot mr-2"></i>
                            Hi! I can help you with air quality health questions. Ask me anything!
                        </div>
                    </div>
                </div>
                <div class="flex">
                    <input type="text" id="health-chat-input" 
                           placeholder="Ask about air quality..." 
                           class="flex-1 px-3 py-2 border rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <button onclick="mlDashboard.sendChatMessage(document.getElementById('health-chat-input').value)" 
                            class="bg-blue-500 text-white px-4 py-2 rounded-r-lg hover:bg-blue-600">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
            </div>
        `;
        
        document.getElementById('health-chat-container').innerHTML = chatHtml;
    }

    async loadInitialMLData() {
        const location = this.getCurrentLocation();
        
        // Load predictions and anomaly data
        await Promise.all([
            this.fetchMLPredictions(location),
            this.checkAnomalies(location)
        ]);
    }

    startRealTimeUpdates() {
        setInterval(() => {
            this.loadInitialMLData();
        }, this.updateInterval);
    }

    getCurrentLocation() {
        return document.getElementById('location-name')?.textContent || 'New York, NY';
    }

    getCurrentAQI() {
        return parseInt(document.getElementById('aqi-value')?.textContent) || 50;
    }

    getCSRFToken() {
            const inputToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            if (inputToken) return inputToken;

            // Fallback to csrftoken cookie
            function getCookie(name) {
                let cookieValue = null;
                if (document.cookie && document.cookie !== '') {
                    const cookies = document.cookie.split(';');
                    for (let i = 0; i < cookies.length; i++) {
                        const cookie = cookies[i].trim();
                        if (cookie.substring(0, name.length + 1) === (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }

            return getCookie('csrftoken') || '';
    }
}

// Initialize ML Dashboard
let mlDashboard;
document.addEventListener('DOMContentLoaded', function() {
    mlDashboard = new MLDashboard();
});

// Add scenario simulation buttons to existing dashboard
document.addEventListener('DOMContentLoaded', function() {
    const scenarioContainer = document.getElementById('scenario-buttons');
    if (scenarioContainer) {
        scenarioContainer.innerHTML = `
            <div class="grid grid-cols-2 gap-3">
                <button data-scenario="wildfire_nearby" class="btn-outline text-sm py-2">
                    <i class="fas fa-fire mr-1"></i>Wildfire Impact
                </button>
                <button data-scenario="heavy_traffic" class="btn-outline text-sm py-2">
                    <i class="fas fa-car mr-1"></i>Traffic Surge
                </button>
                <button data-scenario="strong_winds" class="btn-outline text-sm py-2">
                    <i class="fas fa-wind mr-1"></i>Strong Winds
                </button>
                <button data-scenario="temperature_spike" class="btn-outline text-sm py-2">
                    <i class="fas fa-thermometer-full mr-1"></i>Heat Wave
                </button>
            </div>
        `;
    }
});