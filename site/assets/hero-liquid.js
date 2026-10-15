(()=>{
  'use strict';
  let sharedTexture=null,sharedTextureUrl='';
  function textureSource(image){
    const url=image.currentSrc||image.src;
    if(!url||image.naturalWidth<=960||!document.createElement)return image;
    if(sharedTexture&&sharedTextureUrl===url)return sharedTexture;
    const copy=document.createElement('canvas');
    copy.width=960;copy.height=Math.round(960*image.naturalHeight/image.naturalWidth);
    const context=copy.getContext('2d',{alpha:false});
    if(!context)return image;
    context.drawImage(image,0,0,copy.width,copy.height);
    sharedTexture=copy;sharedTextureUrl=url;return copy;
  }
  function initLiquid(hero){
    const image=hero.querySelector('.hero-artwork'),canvas=hero.querySelector('.hero-liquid');
    if(!image||!canvas)return;
    const root=document.documentElement,systemMotion=matchMedia('(prefers-reduced-motion: reduce)');
    let gl,program,uniforms,parallel,shaders,ready=false,failed=false,lost=false,resizeNeeded=true;
    const duration=5000;
    let frame=null,warmFrame=null,lastTick=null,lastDraw=null,playbackMs=0;
    const bootTime=performance.now();
    let measuredFrames=0,largestOpeningGap=0;

    const vertexSource=`
      attribute vec2 aPosition;
      varying vec2 vUv;
      void main(){vUv=aPosition*.5+.5;gl_Position=vec4(aPosition,0.,1.);}
    `;
    const fragmentSource=`
      #ifdef GL_FRAGMENT_PRECISION_HIGH
      precision highp float;
      #else
      precision mediump float;
      #endif
      uniform sampler2D uImage;
      uniform vec2 uImageSize;
      uniform vec2 uViewSize;
      uniform float uTime;
      uniform float uStrength;
      uniform float uFocus;
      varying vec2 vUv;
      void main(){
        float aspect=uViewSize.x/uViewSize.y;
        vec2 p=vUv*vec2(aspect,1.);
        float t=uTime*.48;
        // Broad, spatially varying waves bend the image locally, not as one plane.
        vec2 flow=vec2(sin(p.y*4.2+p.x*1.3+t),cos(p.x*2.7-p.y*1.4-t*.83));
        flow+=.32*vec2(sin(p.x*3.6-p.y*2.1-t*.74),cos(p.y*4.1+p.x*1.6+t*.68));
        vec2 edge=smoothstep(vec2(0.),vec2(.14,.18),min(vUv,1.-vUv));
        vec2 warped=vUv+flow*vec2(.035,.055)*edge.x*edge.y*uStrength;
        float imageAspect=uImageSize.x/uImageSize.y;
        vec2 cover=vec2(min(aspect/imageAspect,1.),min(imageAspect/aspect,1.));
        vec2 center=vec2(.5+(uFocus-.5)*(1.-cover.x),.5);
        vec2 uv=(warped-.5)*cover+center;
        gl_FragColor=texture2D(uImage,clamp(uv,vec2(.001),vec2(.999)));
      }
    `;

    const reduced=()=>root.dataset.motion==='reduce'||systemMotion.matches;
    const pace=value=>{
      const p=Math.max(0,Math.min(1,value));
      // Start at normal speed; only the ending settles to rest.
      return p+p*p*p*(4+p*(-7+3*p));
    };
    function stop(fallback=false){
      if(frame!==null)cancelAnimationFrame(frame);
      if(warmFrame!==null)cancelAnimationFrame(warmFrame);
      warmFrame=null;
      frame=null;lastTick=null;lastDraw=null;
      if(fallback)hero.classList.remove('has-liquid');
    }
    function fallback(){
      stop(true);failed=true;hero.dataset.liquid='unavailable';
    }
    function shader(type,source){
      const result=gl.createShader(type);
      gl.shaderSource(result,source);gl.compileShader(result);
      if(!parallel&&!gl.getShaderParameter(result,gl.COMPILE_STATUS)){
        gl.deleteShader(result);throw new Error('Liquid shader unavailable');
      }
      return result;
    }
    function initialize(){
      if(ready)return true;
      if(failed||lost||!image.complete||!image.naturalWidth)return false;
      try{
        if(!program){
          gl=canvas.getContext('webgl',{alpha:false,antialias:false,depth:false,stencil:false,
            preserveDrawingBuffer:false,powerPreference:'low-power'});
          if(!gl){fallback();return false;}
          parallel=gl.getExtension?.('KHR_parallel_shader_compile');
          hero.dataset.flowCompile=parallel?'parallel':'standard';
          const vertex=shader(gl.VERTEX_SHADER,vertexSource),fragment=shader(gl.FRAGMENT_SHADER,fragmentSource);
          shaders=[vertex,fragment];
          program=gl.createProgram();gl.attachShader(program,vertex);gl.attachShader(program,fragment);
          gl.linkProgram(program);
        }
        // Poll completion instead of blocking the first visible paint on driver compilation.
        if(parallel&&!gl.getProgramParameter(program,parallel.COMPLETION_STATUS_KHR))return false;
        if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error('Liquid program unavailable');
        shaders.forEach(part=>gl.deleteShader(part));shaders=null;
        gl.useProgram(program);
        const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
        gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,1,1]),gl.STATIC_DRAW);
        const position=gl.getAttribLocation(program,'aPosition');
        gl.enableVertexAttribArray(position);gl.vertexAttribPointer(position,2,gl.FLOAT,false,0,0);
        const texture=gl.createTexture();gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,texture);
        gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
        gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,true);
        gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,textureSource(image));
        if(gl.getError()!==gl.NO_ERROR)throw new Error('Liquid image unavailable');
        uniforms=Object.fromEntries(['uImage','uImageSize','uViewSize','uTime','uStrength','uFocus']
          .map(name=>[name,gl.getUniformLocation(program,name)]));
        gl.uniform1i(uniforms.uImage,0);
        gl.uniform2f(uniforms.uImageSize,image.naturalWidth,image.naturalHeight);
        resizeNeeded=true;ready=true;return true;
      }catch(error){fallback();return false;}
    }
    function resize(){
      if(!resizeNeeded)return;
      const bounds=hero.getBoundingClientRect();
      // Deliberately avoid devicePixelRatio multiplication for a soft backdrop.
      const scale=Math.min(1,960/Math.max(1,bounds.width),640/Math.max(1,bounds.height));
      canvas.width=Math.max(1,Math.round(bounds.width*scale));
      canvas.height=Math.max(1,Math.round(bounds.height*scale));
      gl.viewport(0,0,canvas.width,canvas.height);
      gl.uniform2f(uniforms.uViewSize,canvas.width,canvas.height);
      gl.uniform1f(uniforms.uFocus,window.innerWidth<=760?.68:.5);
      resizeNeeded=false;
    }
    function draw(){
      resize();
      gl.uniform1f(uniforms.uTime,pace(playbackMs/duration)*duration/1000);
      gl.uniform1f(uniforms.uStrength,1);
      gl.drawArrays(gl.TRIANGLE_STRIP,0,4);
    }
    function tick(){
      const now=performance.now();
      if(frame===null)return;
      frame=null;
      if(lastTick!==null){
        const gap=Math.max(0,now-lastTick);
        playbackMs=Math.min(duration,playbackMs+gap);
        if(measuredFrames<30){
          largestOpeningGap=Math.max(largestOpeningGap,gap);measuredFrames++;
          if(measuredFrames===1)hero.dataset.flowFirstFrameMs=String(Math.round(now-bootTime));
          if(measuredFrames===30)hero.dataset.flowOpeningGapMs=String(Math.round(largestOpeningGap));
        }
      }
      lastTick=now;
      // Match the display refresh instead of dropping the opening frames to 24 fps.
      draw();lastDraw=now;
      if(playbackMs===duration){
        // Keep the final rendered image; no loop, fade-out or snap back to the poster.
        stop();hero.dataset.liquid='finished';return;
      }
      frame=requestAnimationFrame(tick);
    }
    function sync(){
      if(reduced()){
        stop(true);hero.dataset.liquid='static';return;
      }
      if(lost||failed){stop(true);hero.dataset.liquid='unavailable';return;}
      if(document.hidden||hero.dataset.motionActive==='false'){
        stop();hero.dataset.liquid=playbackMs===duration?'finished':'paused';return;
      }
      if(!initialize()){
        if(parallel&&!failed&&!lost&&warmFrame===null){
          warmFrame=requestAnimationFrame(()=>{warmFrame=null;sync();});
        }
        return;
      }
      if(frame!==null)return;
      draw();hero.classList.add('has-liquid');
      if(playbackMs===duration){hero.dataset.liquid='finished';return;}
      lastTick=performance.now();lastDraw=lastTick;hero.dataset.liquid='running';
      frame=requestAnimationFrame(tick);
    }
    canvas.addEventListener('webglcontextlost',event=>{
      event.preventDefault();lost=true;ready=false;stop(true);hero.dataset.liquid='unavailable';
    });
    canvas.addEventListener('webglcontextrestored',()=>{lost=false;failed=false;ready=false;program=null;parallel=null;sync();});
    const stateObserver=new MutationObserver(sync);
    stateObserver.observe(root,{attributes:true,attributeFilter:['data-motion']});
    stateObserver.observe(hero,{attributes:true,attributeFilter:['data-motion-active']});
    // Every backdrop has its own visibility budget. Offscreen sections allocate no GPU.
    const bounds=hero.getBoundingClientRect();
    hero.dataset.motionActive=String(bounds.bottom>0&&bounds.top<window.innerHeight);
    if('IntersectionObserver' in window){
      new IntersectionObserver(entries=>{
        for(const entry of entries){
          hero.dataset.motionActive=String(entry.isIntersecting);
          sync();
        }
      },{threshold:0}).observe(hero);
    }
    const onResize=()=>{
      resizeNeeded=true;
      // A stopped canvas still needs one redraw when its layout or GPU backing changes.
      if(ready&&!lost&&!failed&&!reduced()&&frame===null)draw();
    };
    if('ResizeObserver' in window)new ResizeObserver(onResize).observe(hero);
    else window.addEventListener('resize',onResize);
    document.addEventListener('visibilitychange',sync);
    systemMotion.addEventListener('change',sync);
    window.addEventListener('pagehide',()=>{stop();hero.dataset.liquid='paused';});
    window.addEventListener('pageshow',event=>{
      // A cached return is a new visit. Scrolling and tab visibility only pause/resume.
      if(event.persisted){stop();playbackMs=0;}
      sync();
    });
    image.addEventListener('load',sync,{once:true});
    sync();
  }
  const initializeBackdrops=()=>document.querySelectorAll('.hero-panel').forEach(initLiquid);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initializeBackdrops,{once:true});
  else initializeBackdrops();
})();
