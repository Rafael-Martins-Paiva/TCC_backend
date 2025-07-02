# 🚀 Guia de Desenvolvimento do Projeto

Este documento estabelece as diretrizes e convenções a serem seguidas no desenvolvimento deste projeto, garantindo consistência, qualidade e manutenibilidade do código.

---

## 1. 🏛️ Arquitetura e Design

A estrutura do projeto é baseada em princípios sólidos que visam a clareza e a escalabilidade.

-   **Domain-Driven Design (DDD):** Utilize DDD como a principal abordagem para a estruturação do projeto. Mantenha uma separação estrita entre as camadas:
    -   **Domain:** Onde a lógica de negócio principal reside.
    -   **Application:** Orquestra as ações do domínio.
    -   **Infrastructure:** Detalhes de implementação (ex: banco de dados, APIs externas).
    -   **Presentation:** Interface com o usuário (ex: APIs REST).

-   **Programação Orientada a Objetos (OOP):** Crie objetos coesos e com responsabilidades bem definidas. Encapsule a lógica de negócio para criar um domínio rico.

-   **Princípios Fundamentais:**
    -   **SOLID:** Siga rigorosamente os cinco princípios SOLID.
    -   **DRY (Don't Repeat Yourself):** Evite duplicação de código.
    -   **KISS (Keep It Simple, Stupid):** Prefira soluções simples e diretas.
    -   **YAGNI (You Aren’t Gonna Need It):** Não implemente funcionalidades que não são necessárias no momento.

-   **Padrões de Projeto:** Utilize padrões como DTOs, UseCases, Entities e Repositories para manter a organização e a clareza.

-   **Qualidade Arquitetural:**
    -   Construa uma arquitetura limpa, modular e escalável.
    -   Evite "gambiarras" ou "workarounds". Se for estritamente necessário, documente a justificativa de forma clara.

---

## 2. ✨ Qualidade de Código

A legibilidade e a clareza são prioridades.

-   **Código Limpo:** Escreva código que seja fácil de ler e entender. Um código claro é sempre superior a um código "inteligente" e complexo.
-   **Ferramentas de Análise:** Utilize ferramentas de linting, formatação e análise estática (como ESLint, Prettier, SonarQube) para garantir a conformidade com os padrões.

---

## 3. ✍️ Comentários

Comentários devem ser usados com moderação e apenas quando agregam valor.

-   **Código Autoexplicativo:** Esforce-se para que o código se explique por si só.
-   **O "Porquê", não "O Quê":** Se um comentário for indispensável, ele deve explicar a *razão* por trás de uma decisão de implementação, e não o que o código está fazendo.
-   **Evite Redundância:** Nunca escreva comentários que apenas repetem o que o código já diz.

    *Exemplo do que **não** fazer:*
    ```javascript
    // Incrementa o contador em 1
    contador += 1;
    ```

---

## 4. 🧪 Testes

Testes são a espinha dorsal da estabilidade da nossa aplicação.

### Executando Testes

-   **Comando para um app específico:**
    ```bash
    uv run manage.py test tests.nome_do_app
    ```
-   **Comando para todos os testes do projeto:**
    ```bash
    uv run manage.py test
    ```
-   **Consistência:** Mantenha o estilo de teste (`pytest` ou `unittest`) já adotado no projeto.

### Diretrizes para Testes Unitários

1.  **Cobertura Completa:** Valide todos os fluxos do código, incluindo casos de sucesso, falha, dados inválidos e exceções.
2.  **Escopo Abrangente:** Teste todas as camadas: modelos, serializers, views, permissões e regras de negócio.
3.  **Isolamento:** Use mocks e fixtures para isolar o comportamento testado e simular dependências externas.
4.  **Especificidade:** Crie testes com nomes claros e focados em um único comportamento. Evite testes genéricos.
5.  **Assertivas Claras:** Utilize as assertivas mais precisas possíveis (`assertEqual`, `assertContains`, `assertRaises`).
6.  **Foco no Domínio:** Garanta alta cobertura de código, especialmente nas regras de negócio críticas.
7.  **Regressão de Bugs:** Ao corrigir um bug, crie um teste que cubra o cenário do bug para evitar que ele ocorra novamente.

> ⚠️ **Filosofia de Teste:** Um bom teste é rigoroso. Ele deve falhar com a menor inconsistência, pois é essa sensibilidade que garante a robustez e a confiança na aplicação.