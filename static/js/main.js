// Main JavaScript for FitnessApp

// Função para mostrar loading
function showLoading() {
    let overlay = document.querySelector('.spinner-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'spinner-overlay';
        overlay.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Carregando...</span></div>';
        document.body.appendChild(overlay);
    }
    overlay.classList.add('active');
}

function hideLoading() {
    const overlay = document.querySelector('.spinner-overlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
}

// Função para mostrar toast
function showToast(message, type = 'success') {
    const toastDiv = document.createElement('div');
    toastDiv.className = `toast-notification alert alert-${type}`;
    toastDiv.innerHTML = `
        <div class="d-flex align-items-center">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close ms-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    document.body.appendChild(toastDiv);
    
    setTimeout(() => {
        toastDiv.remove();
    }, 3000);
}

// Função para salvar série via AJAX
async function salvarSerie(data) {
    try {
        const response = await fetch('/treino/salvar-serie/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Série salva com sucesso!', 'success');
            return result;
        } else {
            showToast('Erro ao salvar série', 'danger');
            return null;
        }
    } catch (error) {
        console.error('Erro:', error);
        showToast('Erro de conexão', 'danger');
        return null;
    }
}

// Função para carregar dados dos gráficos
async function carregarGraficos(alunoId) {
    showLoading();
    try {
        const response = await fetch(`/api/graficos/${alunoId}/`);
        const data = await response.json();
        
        // Renderizar gráficos
        if (data.avaliacoes) {
            renderEvolucaoChart(data.avaliacoes);
        }
        
        if (data.iet) {
            renderVo2MaxChart(data.iet);
        }
        
        if (data.volume_semanal) {
            renderVolumeChart(data.volume_semanal);
        }
    } catch (error) {
        console.error('Erro ao carregar gráficos:', error);
        showToast('Erro ao carregar dados', 'danger');
    } finally {
        hideLoading();
    }
}

// Função para renderizar gráfico de evolução
function renderEvolucaoChart(data) {
    const canvas = document.getElementById('evolucaoChart');
    if (!canvas) return;
    
    new Chart(canvas, {
        type: 'line',
        data: {
            labels: data.datas,
            datasets: [{
                label: 'Peso (kg)',
                data: data.pesos,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }, {
                label: '% Gordura',
                data: data.percentuais,
                borderColor: 'rgb(255, 99, 132)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });
}

// Função para renderizar gráfico de VO2 Max
function renderVo2MaxChart(data) {
    const canvas = document.getElementById('vo2maxChart');
    if (!canvas) return;
    
    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: data.datas,
            datasets: [{
                label: 'VO2 Máx (ml/kg/min)',
                data: data.vo2_max,
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Função para renderizar gráfico de volume
function renderVolumeChart(data) {
    const canvas = document.getElementById('volumeChart');
    if (!canvas) return;
    
    const semanas = Object.keys(data);
    const volumes = Object.values(data);
    
    new Chart(canvas, {
        type: 'line',
        data: {
            labels: semanas.map(s => `Semana ${s}`),
            datasets: [{
                label: 'Volume Total (kg)',
                data: volumes,
                borderColor: 'rgb(255, 159, 64)',
                backgroundColor: 'rgba(255, 159, 64, 0.2)',
                fill: true,
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.raw.toFixed(0)} kg`;
                        }
                    }
                }
            }
        }
    });
}

// Função auxiliar para pegar CSRF token
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

// Máscara para inputs
function mascaraPeso(input) {
    let value = input.value.replace(/\D/g, '');
    if (value.length > 3) {
        value = value.slice(0, -2) + '.' + value.slice(-2);
    }
    input.value = value;
}

function mascaraAltura(input) {
    let value = input.value.replace(/\D/g, '');
    if (value.length > 2) {
        value = value.slice(0, -2) + '.' + value.slice(-2);
    }
    input.value = value;
}

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    // Adicionar máscaras aos inputs
    const pesoInputs = document.querySelectorAll('input[name="massa_corporal"]');
    pesoInputs.forEach(input => {
        input.addEventListener('input', () => mascaraPeso(input));
    });
    
    const alturaInputs = document.querySelectorAll('input[name="altura"]');
    alturaInputs.forEach(input => {
        input.addEventListener('input', () => mascaraAltura(input));
    });
    
    // Auto-save no treino (opcional)
    const autoSave = document.querySelector('#auto-save-toggle');
    if (autoSave && autoSave.checked) {
        setInterval(() => {
            // Salvar automaticamente as séries
            document.querySelectorAll('.serie-row').forEach(row => {
                const cargaInput = row.querySelector('.carga-input');
                if (cargaInput && cargaInput.value) {
                    // Lógica para salvar automaticamente
                }
            });
        }, 30000); // A cada 30 segundos
    }
});