# Models

<!-- ============================================================
  01 · KAT-Coder-V2.5-Dev · Open-weight release
============================================================ -->
<section class="open-model-card" data-hf-model="Kwaipilot/KAT-Coder-V2.5-Dev" aria-labelledby="kat-coder-v25-dev-title">
  <div class="open-model-card__header">
    <div>
      <h2 id="kat-coder-v25-dev-title">KAT-Coder-V2.5-Dev</h2>
    </div>
    <div class="open-model-card__header-tools">
      <div class="hf-model-stats" aria-live="polite" aria-label="Hugging Face model statistics">
        <div class="hf-model-stat" title="KAT-Coder-V2.5-Dev all-time downloads">
          <i class="fas fa-download hf-model-stat__icon" aria-hidden="true"></i>
          <span class="hf-model-stat__value" data-hf-stat="downloads-all-time">17,399</span>
          <span class="visually-hidden"> model all-time downloads</span>
        </div>
        <div class="hf-model-stat" title="Total all-time downloads including derived models">
          <i class="fas fa-layer-group hf-model-stat__icon" aria-hidden="true"></i>
          <span class="hf-model-stat__value" data-hf-stat="ecosystem-downloads-all-time">420,630</span>
          <span class="visually-hidden"> total all-time downloads including derived models</span>
        </div>
        <div class="hf-model-stat" title="Likes">
          <i class="fas fa-heart hf-model-stat__icon" aria-hidden="true"></i>
          <span class="hf-model-stat__value" data-hf-stat="likes">523</span>
          <span class="visually-hidden"> likes</span>
        </div>
        <a class="hf-model-stat hf-model-stat--link" href="https://huggingface.co/Kwaipilot/KAT-Coder-V2.5-Dev" target="_blank" rel="noopener noreferrer">
          <img class="hf-model-stat__brand-icon" src="/images/huggingface.svg" alt="" aria-hidden="true">
          <span>Hugging Face</span>
        </a>
      </div>
    </div>
  </div>

  <p class="open-model-card__summary">A lightweight 35B-A3B MoE variant of KAT-Coder-V2.5, built for long-horizon agentic coding.</p>

  <ul class="open-model-card__highlights">
    <li><strong>Agentic coding:</strong> 69.4% on SWE-bench Verified and 93.4% on PinchBench.</li>
    <li><strong>Long-context:</strong> native support for up to 1M tokens for longer-context serving.</li>
    <li><strong>Reliable tool use:</strong> fewer malformed tool labels and repetitive single-turn behaviors.</li>
  </ul>

</section>

<!-- ============================================================
  02 · KAT-Coder-V2.5
============================================================ -->
<div class='paper-box'>
  <div class='paper-box-image'><div>
    <div class="badge">KAT-Coder-V2.5</div>
    <picture><source srcset="/images/papers/katcoder_v2.5.webp" type="image/webp"><img loading="lazy" src="/images/papers/katcoder_v2.5.png" alt="KAT-Coder-V2.5 teaser" width="100%"></picture>
  </div></div>
  <div class='paper-box-text' markdown="1">

<span class="title-with-logo"><svg class="tr-logo" viewBox="0 0 127.73 74.83" role="img" aria-label="KAT logo" xmlns="http://www.w3.org/2000/svg"><path fill="#000" d="M31.008 32.516V12.992c0-1.219.988-2.207 2.207-2.207h61.031c1.219 0 2.203.988 2.203 2.207v19.524h10.789V12.992C107.238 5.828 101.41 0 94.246 0H33.215C26.051 0 20.223 5.828 20.223 12.992v19.524z"></path><path fill="#000" d="M96.449 42.145v19.523c0 1.219-.984 2.207-2.203 2.207H33.215c-1.219 0-2.207-.988-2.207-2.207V42.145H20.223v19.523c0 7.164 5.828 12.992 12.992 12.992h61.031c7.164 0 12.992-5.828 12.992-12.992V42.145z"></path><path fill="#489034" d="M42.863 31 .012 15.324v12.223l26.847 9.816L.012 47.184v12.222L42.863 43.742z"></path><path fill="#489034" d="M84.598 31l42.851-15.676v12.223l-26.848 9.816 26.848 9.821v12.222L84.598 43.742z"></path><path fill="#489034" d="M72.496 27.488H60.812l-5.847 19.266h11.683z"></path></svg><strong>KAT-Coder-V2.5 Technical Report</strong></span>

KwaiKAT Team, Kuaishou Technology

<a class="resource-link" href="https://arxiv.org/abs/2607.05471"><i class="fas fa-file-alt resource-link__icon" aria-hidden="true"></i>Paper</a> <a class="resource-link" href="https://mp.weixin.qq.com/s/Ylz2hAbKs9gm5CXMfavIxw"><i class="fab fa-weixin resource-link__icon" aria-hidden="true"></i>News</a>

- KAT-Coder-V2.5 achieves 65.2% on SWE-bench Pro (vs. Claude Opus 4.8 at 69.2%), 94.2% on PinchBench (vs. Claude Opus 4.8 at 93.5%)
- KAT-Coder-V2.5 surpassing GLM-5.1, approaching GLM-5.2
</div>
</div>

<!-- ============================================================
  02 · KAT-Coder-V2
============================================================ -->
<div class='paper-box'>
  <div class='paper-box-image'><div>
    <div class="badge">KAT-Coder-V2</div>
    <picture><source srcset="/images/papers/katcoder_v2.webp" type="image/webp"><img loading="lazy" src="/images/papers/katcoder_v2.png" alt="KAT-Coder-V2 teaser" width="100%"></picture>
  </div></div>
  <div class='paper-box-text' markdown="1">

<span class="title-with-logo"><svg class="tr-logo" viewBox="0 0 127.73 74.83" role="img" aria-label="KAT logo" xmlns="http://www.w3.org/2000/svg"><path fill="#000" d="M31.008 32.516V12.992c0-1.219.988-2.207 2.207-2.207h61.031c1.219 0 2.203.988 2.203 2.207v19.524h10.789V12.992C107.238 5.828 101.41 0 94.246 0H33.215C26.051 0 20.223 5.828 20.223 12.992v19.524z"></path><path fill="#000" d="M96.449 42.145v19.523c0 1.219-.984 2.207-2.203 2.207H33.215c-1.219 0-2.207-.988-2.207-2.207V42.145H20.223v19.523c0 7.164 5.828 12.992 12.992 12.992h61.031c7.164 0 12.992-5.828 12.992-12.992V42.145z"></path><path fill="#489034" d="M42.863 31 .012 15.324v12.223l26.847 9.816L.012 47.184v12.222L42.863 43.742z"></path><path fill="#489034" d="M84.598 31l42.851-15.676v12.223l-26.848 9.816 26.848 9.821v12.222L84.598 43.742z"></path><path fill="#489034" d="M72.496 27.488H60.812l-5.847 19.266h11.683z"></path></svg><strong>KAT-Coder-V2 Technical Report</strong></span>

KwaiKAT Team, Kuaishou Technology

<a class="resource-link" href="https://arxiv.org/abs/2603.27703"><i class="fas fa-file-alt resource-link__icon" aria-hidden="true"></i>Paper</a> <a class="resource-link" href="https://mp.weixin.qq.com/s/PGWZfZFGp19QdAGuRE-APg"><i class="fab fa-weixin resource-link__icon" aria-hidden="true"></i>News</a>

- KAT-Coder-V2 ranks 6th on Artificial Analysis Coding Index
- KAT-Coder-V2 achieves 79.6% on SWE-bench Verified (vs. Claude Opus 4.6 at 80.8%); 88.7% on PinchBench (surpassing GLM-5 and MiniMax M2.7)
</div>
</div>


<!-- ============================================================
  03 · LPM
============================================================ -->
<div class='paper-box'>
  <div class='paper-box-image'><div>
    <div class="badge">LPM</div>
    <picture><source srcset="/images/papers/lpm.webp" type="image/webp"><img loading="lazy" src="/images/papers/lpm.png" alt="LPM teaser" width="100%"></picture>
  </div></div>
  <div class='paper-box-text' markdown="1">

<span class="title-with-logo"><strong>LPM: Industrial-Scale Generative Video Restoration</strong></span>

LPM Team, Kuaishou Technology

<a class="resource-link" href="https://arxiv.org/abs/2607.13460"><i class="fas fa-file-alt resource-link__icon" aria-hidden="true"></i>Paper</a>

- Large Processing Model (LPM) is a diffusion-based generative framework for photorealistic video restoration
- To our knowledge, LPM is the first generative video restoration model deployed at industrial scale
</div>
</div>
