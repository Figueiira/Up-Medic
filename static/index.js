document.addEventListener('DOMContentLoaded', () => {
  const inputData = document.getElementById('data');
  const selectHorario = document.getElementById('horario');

  // Disponibilidades enviadas via contexto Flask
  const DISPONIBILIDADES = JSON.parse('{{ disponibilidades | tojson | safe }}');

  inputData.addEventListener('change', () => {
    const dataSelecionada = inputData.value;
    const horarios = DISPONIBILIDADES[dataSelecionada] || [];

    // Limpa o select
    selectHorario.innerHTML = '';

    if (horarios.length === 0) {
      const option = document.createElement('option');
      option.textContent = 'Sem horários disponíveis';
      option.disabled = true;
      selectHorario.appendChild(option);
      return;
    }

    horarios.forEach(horario => {
      const option = document.createElement('option');
      option.value = horario;
      option.textContent = horario;
      selectHorario.appendChild(option);
    });
  });
});
