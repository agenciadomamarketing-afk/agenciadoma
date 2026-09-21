# Doma Food — atualização visual

Pacote de substituição com 11 arquivos completos. Não é um projeto autônomo.

## Aplicar

1. Guarde uma cópia do projeto atual.
2. Copie `app.py`, `utils/` e `pages/` deste pacote para a raiz do projeto existente, mesclando as pastas e substituindo somente os arquivos de mesmo nome.
3. Preserve `utils/data.py`, `utils/__init__.py`, `assets/`, `requirements.txt` e `.streamlit/` atuais. O pacote não inclui credenciais e não substitui esses arquivos.
4. Execute `streamlit run app.py` na raiz do projeto. Para publicar, envie os arquivos modificados pelo seu fluxo habitual.

Os arquivos do repositório original e a aplicação publicada não foram alterados.

## Tabelas e compatibilidade

A visualização HTML apresenta cabeçalho vermelho e linhas alternadas. A tabela interativa original continua disponível no expansor “Ordenar, pesquisar e consultar dados”, com os mesmos dados e controles nativos. Para conjuntos maiores, a prévia HTML mostra até 200 linhas e o expansor contém todas as linhas. Isso evita depender de estilos de cabeçalho não suportados pelo `st.dataframe` em Streamlit 1.35.

Referência técnica: https://docs.streamlit.io/1.35.0/develop/api-reference/data/st.dataframe

O CSS usa seletores internos do Streamlit para a sidebar e o card do login; futuras mudanças de estrutura do Streamlit podem exigir pequenos ajustes. A validação foi feita em Streamlit 1.35.0 e Plotly 5.22.0, não em todas as versões posteriores.

## Validação

Verificações de sintaxe e assinaturas existentes; comparação dos imports de utils.data, atribuições, condições e chamadas de dados das páginas; equivalência dos valores dos gráficos e limites dos gauges; execução das oito telas, login correto/incorreto, logout e ausência de loja com dados fictícios. A conexão real com Google Sheets não faz parte dessa validação visual.

As regras de negócio e os textos interpretativos existentes foram mantidos conforme solicitado. Essa entrega não audita a metodologia financeira.

## Arquivos e alterações

### utils/styles.py

Sistema visual central: tipografia Segoe UI, títulos maiores, cards com borda em gradiente, sidebar com hover vermelho e foco de teclado, alertas HTML com texto escapado, tabelas zebra com cabeçalho vermelho, ajustes para telas pequenas e redução de movimento. Novos auxiliares render_alert, render_table e render_navigation.

### utils/charts.py

Mantidas as assinaturas de kpi, funnel, trend, waterfall e gauge. Cards com ícone discreto e contraste maior; linhas em vermelho Doma, rosa e tons neutros, com traçados distintos; waterfall com cores mais claras e espaço para rótulos; gauge com número maior e marcador da meta. Nova função style_figure para padronizar a apresentação. Valores e regras dos gráficos preservados.

### utils/auth.py

Logo, título, campo de senha e botão reunidos em um único card com gradiente sutil. Mensagem de erro personalizada. Verificação de senha, estado autenticado, retorno, logout e rerun preservados.

### app.py

Cards de entrada padronizados e navegação nativa posicionada depois dos filtros da sidebar. Seletor, período, contagem de lojas e carregamento de dados preservados.

### pages/1_Visao_Geral.py

Navegação abaixo dos filtros, alertas personalizados e tema explícito dos gráficos. Agregações, comparações e textos das interpretações preservados.

### pages/2_Funil.py

Funil com nova paleta, tabela com cabeçalho vermelho e linhas alternadas, alertas personalizados e navegação. Etapas, valores e cálculos de conversão/abandono preservados.

### pages/3_Financeiro.py

Cards e waterfall recebem o novo tema; navegação e alerta de seleção personalizados. Valores, composição financeira, filtros e cálculos preservados.

### pages/4_Operacional.py

Gauges e cards com novo acabamento, alertas HTML e navegação. Limiares, fórmulas dos indicadores e condições dos alertas preservados.

### pages/5_Promocoes.py

Ranking com apresentação zebra e cabeçalho vermelho, alertas HTML e navegação. Fórmula de veredito, subsídios e ordenação preservados.

### pages/6_Clientes.py

Rosca em vermelho e cinza claro, gráfico de tendência consistente, alertas HTML e navegação. Classificações, valores e cálculos preservados.

### pages/7_Chamados.py

Tabela estilizada, gráfico com tipografia unificada, alertas HTML e navegação. Cores semânticas dos status, contagens e ordenação preservadas.
