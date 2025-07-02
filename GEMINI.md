# Organização

- Sempre utilize **DDD (Domain-Driven Design)** como base estrutural do projeto, favorecendo uma separação clara entre camadas (Domínio, Aplicação, Infraestrutura, Apresentação).
- Aplique **programação orientada a objetos (OOP)** de maneira disciplinada. Foque na criação de objetos ricos e coesos, encapsulando lógica de negócio.
- Use e respeite os princípios **SOLID** (responsabilidade única, aberto/fechado, substituição de Liskov, segregação de interfaces, inversão de dependências).
- Siga as boas práticas **DRY (Don't Repeat Yourself)**, **KISS (Keep It Simple, Stupid)** e **YAGNI (You Aren’t Gonna Need It)**.
- Crie uma arquitetura **limpa**, modular e escalável. Mantenha os arquivos, pastas e responsabilidades organizadas e bem definidas.
- Documente a estrutura do projeto em arquivos como este, para facilitar o entendimento e a manutenção.
- Use padrões como **DTOs, UseCases, Entities, Repositories**, sempre que fizer sentido.
- Evite qualquer tipo de "gambiarra" ou "workaround" sem uma justificativa clara e documentada.
- Priorize a clareza e a legibilidade do código acima de tudo. Um código limpo é melhor que um código "esperto".
- Use ferramentas de linting, formatação automática e análise estática de código sempre que possível (Ex: ESLint, Prettier, SonarQube).

# Comentários

- **Nunca** escreva comentários desnecessários no código. O código deve ser **autoexplicativo**.
- Se um comentário for absolutamente necessário, ele deve explicar o **porquê** de algo, não **o que** está sendo feito.
- Evite comentários redundantes como:
  ```js
  // incrementa 1
  contador += 1;

- Use `pytest` ou `unittest` de forma consistente, conforme já adotado no projeto. A não ser que seja **explicitamente solicitado**, **não mude o estilo atual** dos testes.
- Para executar os testes, utilize:
- `uv run manage.py test tests.nome do app` → testa apenas o app.
- `uv run manage.py test` → executa todos os testes do projeto.

## Regras para testes unitários pesados

1. **Valide todos os caminhos do código**, incluindo:
 - Casos válidos e inválidos
 - Dados ausentes, nulos ou incorretos
 - Lógicas condicionais, loops, erros esperados e exceções
2. **Cubra modelos, serializers, views, permissões e regras de negócio**.
3. **Use mocks ou fixtures** sempre que precisar isolar o comportamento ou simular dependências.
4. **Evite testes genéricos**. Cada teste deve ter um nome claro e checar um único comportamento.
5. **Use assertivas precisas** e claras (`assertEqual`, `assertContains`, `assertRaises`, etc.).
6. **Garanta alta cobertura de código**, especialmente em código de domínio e regras de negócio.
7. **Sempre escreva testes para bugs corrigidos**, garantindo que não voltem a acontecer no futuro.

> ⚠️ Teste pesado é teste que não perdoa erro. Ele quebra por coisa mínima — e é exatamente isso que garante a estabilidade da aplicação.

