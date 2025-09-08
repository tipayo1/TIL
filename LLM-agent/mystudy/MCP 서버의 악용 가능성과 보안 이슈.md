<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

### MCP 서버의 악용 가능성과 보안 이슈

#### 1. 악의적 MCP 서버 및 악성 정보 업로드 가능성

- **누구나 MCP 서버를 직접 만들어 배포할 수 있으며, 검증되지 않은 MCP 서버에 악의적 코드나 정보를 숨겨 배포하는 사례가 실제로 보고되고 있습니다.**
예를 들어, 공격자는 정상적인 도구처럼 보이는 MCP 서버를 만들어 공개 저장소나 개발자 커뮤니티에 업로드할 수 있습니다. 사용자가 이를 신뢰하고 설치하면, 내부적으로 악성 코드를 실행하거나 시스템에 백도어를 설치할 수 있습니다[^1][^2][^3].
- **MCP 서버의 도구 설명이나 프롬프트 템플릿에 악의적 명령을 숨기는 것도 가능합니다.**
예를 들어, 도구 설명에 "특정 단어 입력 시 대화 로그를 외부 서버로 전송" 같은 명령을 숨겨두고, 사용자가 특정 단어를 입력하면 민감한 정보가 유출될 수 있습니다[^3][^4].


#### 2. 주요 보안 이슈

- **명령어/코드 인젝션**
입력값 검증이 미흡한 MCP 서버는 공격자가 임의의 시스템 명령을 실행하게 만들 수 있습니다. 실제로 수많은 MCP 서버가 명령어 인젝션, 경로 탐색, 임의 파일 읽기 등 심각한 취약점을 가지고 있는 것으로 조사되었습니다[^5][^6][^7][^8].
- **프롬프트 인젝션 및 컨텍스트 오염**
악의적 데이터(문서, 티켓 등)를 LLM에 전달해, AI가 의도치 않은 행동(정보 유출, 권한 상승 등)을 하도록 유도할 수 있습니다[^4][^9][^6].
- **과도한 권한 및 인증/인가 미흡**
일부 MCP 서버는 필요 이상의 권한을 부여받아, 공격 시 더 많은 시스템/데이터에 접근할 수 있습니다. 인증·인가가 제대로 구현되지 않으면, 누구나 MCP 서버를 통해 민감 정보에 접근할 수 있습니다[^10][^11][^12].
- **공급망 공격**
MCP 서버 코드 자체에 악성코드가 포함될 수 있으며, 공식 저장소가 없는 경우 신뢰할 수 없는 MCP 서버가 유통될 위험이 큽니다[^1][^12].
- **Shadow MCP(그림자 MCP) 문제**
보안팀의 관리 밖에서 설치된 MCP 서버가 조직 내 보안 사각지대를 만들고, 공격자가 이를 악용해 내부 시스템에 침투할 수 있습니다[^3].


#### 3. MCP 서버가 내 정보를 빼갈 위험

- **실제로 MCP 서버가 내 정보를 빼갈 수 있는 구조적 위험이 존재합니다.**
    - MCP 서버는 다양한 외부 서비스(이메일, 파일, DB 등)에 접근할 수 있는 인증 토큰이나 API 키를 저장합니다. 공격자가 MCP 서버를 탈취하거나 악성 MCP를 설치하면, 이 토큰을 통해 사용자의 여러 서비스 데이터에 접근·유출할 수 있습니다[^11][^9][^2].
    - 악성 MCP 서버 또는 취약한 MCP 서버는 사용자의 파일, 대화 내용, 인증 정보 등을 외부로 전송하거나, 추가 악성코드를 설치할 수 있습니다[^1][^2][^6].
    - 특히, 프롬프트 인젝션·명령어 인젝션 등으로 사용자가 인지하지 못하는 사이에 데이터가 외부로 유출될 수 있습니다[^4][^6].


#### 4. 안전하게 MCP 서버를 사용하려면

- 신뢰할 수 있는 공식 저장소에서만 MCP 서버를 설치하고, 디지털 서명 등 무결성 검증을 반드시 수행해야 합니다[^1][^12].
- MCP 서버의 권한을 최소화하고, 불필요한 시스템/데이터 접근 권한을 제거해야 합니다[^10][^11][^4].
- 입력값 검증, 인증·인가, 로그 모니터링 등 기본적인 보안 조치를 철저히 적용해야 합니다[^4][^3][^12].
- 새로운 MCP 서버나 도구를 도입할 때는 반드시 보안팀의 검토와 승인을 거쳐야 하며, 그림자 MCP 설치를 방지해야 합니다[^3].

**결론:**
MCP 서버는 누구나 만들 수 있고, 악의적으로 악성 정보를 포함하거나 내 정보를 빼가는 데 악용될 수 있습니다. 실제로 다양한 보안 이슈와 악용 사례가 보고되고 있으므로, MCP 서버 사용 시 신뢰성과 보안성을 반드시 검증해야 합니다.

<div style="text-align: center">⁂</div>

[^1]: https://live.paloaltonetworks.com/t5/community-blogs/mcp-security-exposed-what-you-need-to-know-now/ba-p/1227143

[^2]: https://www.catonetworks.com/blog/cato-ctrl-exploiting-model-context-protocol-mcp/

[^3]: https://techcommunity.microsoft.com/blog/microsoftdefendercloudblog/plug-play-and-prey-the-security-risks-of-the-model-context-protocol/4410829

[^4]: https://www.prompt.security/blog/top-10-mcp-security-risks

[^5]: https://equixly.com/blog/2025/03/29/mcp-server-new-security-nightmare/

[^6]: https://www.backslash.security/blog/hundreds-of-mcp-servers-vulnerable-to-abuse

[^7]: https://www.infosecurity-magazine.com/news/mcp-servers-risk-rce-data-leaks/

[^8]: https://www.darkreading.com/cloud-security/hundreds-mcp-servers-ai-models-abuse-rce

[^9]: https://www.upwind.io/feed/unpacking-the-security-risks-of-model-context-protocol-mcp-servers

[^10]: https://techcommunity.microsoft.com/blog/microsoft-security-blog/understanding-and-mitigating-security-risks-in-mcp-implementations/4404667

[^11]: https://www.pillar.security/blog/the-security-risks-of-model-context-protocol-mcp

[^12]: https://www.redhat.com/en/blog/model-context-protocol-mcp-understanding-security-risks-and-controls

[^13]: https://www.trendmicro.com/en_dk/research/25/f/why-a-classic-mcp-server-vulnerability-can-undermine-your-entire-ai-agent.html

[^14]: https://www.backslash.security/blog/top-risks-mcp-servers-ide

[^15]: https://www.trendmicro.com/ko_kr/research/25/f/why-a-classic-mcp-server-vulnerability-can-undermine-your-entire-ai-agent.html

[^16]: https://www.reddit.com/r/mcp/comments/1jr7sfc/mcp_is_a_security_nightmare/

[^17]: https://sysdig.com/blog/why-mcp-server-security-is-critical-for-ai-driven-enterprises/

[^18]: https://www.cyberark.com/resources/threat-research-blog/poison-everywhere-no-output-from-your-mcp-server-is-safe

