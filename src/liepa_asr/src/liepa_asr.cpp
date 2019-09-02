#include "liepa_asr.h"
#include <qi/log.hpp>


LiepaASR::LiepaASR(qi::SessionPtr session)
  : _session(session)
{
  qi::AnyObject almemory = _session->service("ALMemory");
  almemory.async<qi::AnyObject>("declareEvent", "LiepaWordRecognized");
  almemory.async<qi::AnyObject>("declareEvent", "LiepaWordRecognizedNOT");
}
/**
 * 
 */
std::string LiepaASR::version() const
{
  qiLogInfo("LiepaASR.version") << "version method called. "<< __TIMESTAMP__ <<"\n";
  qiLogInfo("LiepaASR.version") << "acousticModel. "<< hmmPath << __TIMESTAMP__ <<"\n";
  qiLogInfo("LiepaASR.version") << "grammarPath. "<< grammarPath << __TIMESTAMP__ <<"\n";
  qiLogInfo("LiepaASR.version") << "dictionaryPath. "<< dictionaryPath << __TIMESTAMP__ <<"\n";
  return __TIMESTAMP__;
}



/**
 * 
 **/
std::string LiepaASR::setGrammarPath(std::string pGrammarPath) const{
  grammarPath = pGrammarPath;
  //if pocketsphinx already working, but model is chainging, we need reinitialize it. 
  if(isInitialized){
    isModelChanged = true;
  }
  
  qiLogInfo("LiepaASR.setGrammarPath") << "grammar set "  <<  pGrammarPath << std::endl;;
  return "Grammar set: " + pGrammarPath;
}

/**
 * 
 **/
std::string LiepaASR::setAcousticModelPath(std::string pHmmPath) const{
  hmmPath = pHmmPath;
  //if pocketsphinx already working, but model is chainging, we need reinitialize it. 
  if(isInitialized){
    isModelChanged = true;
  }
  
  qiLogInfo("LiepaASR.setAcousticModelPath") << "acoustic model set "  <<  pHmmPath << std::endl;;
  return "Acoustic model set: " + pHmmPath;
}


/**
 * 
 */
std::string LiepaASR::setDictionaryPath(std::string pDictionaryPath) const{
  dictionaryPath = pDictionaryPath;
  //if pocketsphinx already working, but model is chainging, we need reinitialize it. 
  if(isInitialized){
    isModelChanged = true;
  }
  qiLogInfo("LiepaASR.setDictionaryPath") << "dictionary set "  <<  pDictionaryPath << std::endl;;
  return "Dictionary set: "  + pDictionaryPath;
}

std::string LiepaASR::setVadThreshold(std::string pVadThreshold) const{
  vadThreshold = pVadThreshold;
  return pVadThreshold;
}

std::string LiepaASR::setVadPreSpeech(std::string pVadPreSpeech) const{
  vadPreSpeech = pVadPreSpeech;
  return pVadPreSpeech;
}

std::string LiepaASR::setVadStartSpeech(std::string pVadStartSpeech) const{
  vadStartSpeech = pVadStartSpeech;
  return pVadStartSpeech;
}

std::string LiepaASR::setVadPostSpeech(std::string pVadPostSpeech) const{
  vadPostSpeech = pVadPostSpeech;
  return pVadPostSpeech;
}
  
std::string LiepaASR::setSilenceProbability(std::string pSilenceProbability) const{
  silenceProbability = pSilenceProbability;
  return silenceProbability;
}

/**
 * 
 */
std::string LiepaASR::init() const
{
  
  qiLogInfo("LiepaASR.init") << "init method called " << std::endl;
  ////////////// SPHINX //////////////////////////
  isInSpeech = false;
  isInRecognitionLock = false;
  cmd_ln_t *config;
  config = cmd_ln_init(NULL, ps_args(), TRUE,                   // Load the configuration structure - ps_args() passes the default values
      //"-hmm", "/home/nao/naoqi/lib/LiepaASRResources/liepa-2019_garsynas_3.0and1_56_ZR-01.3_37.cd_ptm_4000",  // path to the standard english language model
      "-hmm", hmmPath,  // path to the standard english language model
      "-jsgf", grammarPath.c_str(),                                         // custom language model (file must be present)
      "-dict", dictionaryPath.c_str(),                                      // custom dictionary (file must be present)
      "-vad_threshold", vadThreshold.c_str(),
      "-vad_prespeech", vadPreSpeech.c_str(),
      "-vad_postspeech", vadPostSpeech.c_str(),
      "-silprob", silenceProbability.c_str(),
      // "-backtrace", "yes",
      // "-rawlogdir", "/tmp/liepa_asr_raw",
      // "-logfn", "/dev/null",                                      // suppress log info from being sent to screen
      NULL);
  decoder = ps_init(config);
  ////////////// /SPHINX /////////////////////////
    qi::AnyObject  audio_service = _session->service("ALAudioDevice");
  
  //ask for the front microphone signal sampled at 16kHz
  //if you want the 4 channels call setClientPreferences(self.module_name, 48000, 0, 0)
  audio_service.call<void>(
            "setClientPreferences",
            "LiepaASR",
            16000,//Hz
            3,//front mic
            0
  ); 
  
  audio_service.call<void>("subscribe","LiepaASR");

  isInitialized = true;
  return "Initialized";
}



/**
 * 
 */
std::string LiepaASR::start() const
{
  // std::cout << "start method called.\n";
  qiLogInfo("LiepaASR.recognition") << "start method called " << std::endl;
  if(isModelChanged){
    shutdown();
  }
  if(!isInitialized){
    qiLogInfo("LiepaASR.recognition") << "start decoder is null.\n";
    init();
  }
  isInSpeech = false;
  isModelChanged = false;
  recordWindowRemaining = 2;
  remainingSamples = 6400;//0.4sec    
  int startedResult = ps_start_utt(decoder);
  isUttStarted = true;
  std::string message = "started";    
  return message;
}
/**
 * 
 */
std::string LiepaASR::pause() const
{
    qiLogInfo("LiepaASR.recognition") << "pause method called " << std::endl;;
    // std::cout << "[LiepaASR][pause] method called.\n";

    std::string message = "pause on listening";
    int result = -1;
    result = ps_end_utt(decoder);
    isUttStarted = false;
    // std::cout << "[LiepaASR][pause] ps_end_utt .\n";
    isInSpeech = false;
    isInRecognitionLock = false;
   
    return message;
}

std::string LiepaASR::shutdown() const
{
    qiLogInfo("LiepaASR.recognition") << "shutdown method called " << std::endl;;
    qi::AnyObject  audio_service = _session->service("ALAudioDevice");
    // std::cout << "[LiepaASR][shutdown] got instance audio_service .\n";

    audio_service.call<void>("unsubscribe", "LiepaASR");
    // std::cout << "[LiepaASR][shutdown] unsubscribe audio_service .\n";

    if(isInitialized){
      ps_free(decoder);
      // cmd_ln_free_r(config);
      isInitialized = false;
      isModelChanged = false;
    }
   
    std::string message = "service listening turned off";

    return message;
}


void LiepaASR::processRemote(int nbOfChannels, int samplesByChannel, qi::AnyValue altimestamp, qi::AnyValue buffer){


  std::pair<char*, size_t> buffer_pointer = buffer.asRaw();
  int16_t* remoteBuffer = (int16_t*)buffer_pointer.first;
  int bufferSize = nbOfChannels * samplesByChannel;
  std::vector<int16_t> channelBuffer = std::vector<int16_t>(remoteBuffer, remoteBuffer+bufferSize);  
  char const *hyp;                   // pointer to "hypothesis" (best guess at the decoded result)
  int32 score;
  bool isCurrentInSpeech = false;

  //////////////// SPHINX //////////////////////////

  if(isInRecognitionLock){
    qiLogInfo("LiepaASR.recognition") << "[LiepaASR][processRemote] isInRecognitionLock skip listening" << std::endl;
    return;
  }
  if(!isUttStarted){
    // std::cout << "[LiepaASR][processRemote] isUttStarted not started. skip listening" << std::endl;
    return;
  }
  if(recordWindowRemaining > 0){
    // std::cout << "[LiepaASR][processRemote] warming up do not process yet. windows to be processed: " << recordWindowRemaining << std::endl;
    recordWindowRemaining--;
    return;
  }


  remainingSamples -= bufferSize;
  // std::cout << "[LiepaASR][processRemote] bufferSize = " << bufferSize << std::endl;
    
  if(remainingSamples > 0){
    // std::cout << "[LiepaASR][processRemote] Filling up the buffer. remainingSamples: " << remainingSamples << std::endl;
    audioBuffer.insert(audioBuffer.end(), channelBuffer.begin(), channelBuffer.end());
    // nanosleep((const struct timespec[]){{0, 10000000L}}, NULL);//0.01sec
    return;
  }else{
    int16_t* bufferArr = &audioBuffer[0];
    ps_process_raw(decoder, bufferArr, audioBuffer.size(), false, false);
    remainingSamples = 6400;
    audioBuffer.clear();
  }
  

  isCurrentInSpeech = ps_get_in_speech(decoder);

  if (isCurrentInSpeech && !isInSpeech) {             // if speech has started and utt_started flag is false                           
      isInSpeech = true;                      // then set the flag
      // std::cout << "[LiepaASR][processRemote] Speech started "<< std::endl;
  }else if (!isCurrentInSpeech && isInSpeech) {             // if speech has ended and the utt_started flag is true
      isInRecognitionLock = true;
      // std::cout << "[LiepaASR][processRemote] ++++++++++++++ Speech ended. start recognition "<< std::endl;
      ps_end_utt(decoder);                          // then mark the end of the utterance
      isUttStarted = false;
      // std::cout << "[LiepaASR][processRemote] Speech ps_end_utt "<< std::endl;
      hyp = ps_get_hyp(decoder, &score );             // query pocketsphinx for "hypothesis" of decoded statement
      qi::AnyObject almemory = _session->service("ALMemory");
      if (hyp != NULL){
        countSequentialFailures = 0;
        qiLogInfo("LiepaASR.recognition") << "[LiepaASR][processRemote] final hyp = " << std::string(hyp) << std::endl;
        almemory.async<qi::AnyObject>("raiseEvent", "LiepaWordRecognized", std::string(hyp));
      }else{
        countSequentialFailures++;
        qiLogInfo("LiepaASR.recognition") << "[LiepaASR][processRemote] hyp is NULL " << std::endl;
        almemory.async<qi::AnyObject>("raiseEvent", "LiepaWordRecognizedNOT", countSequentialFailures);
        
      }
      
      // std::cout << "[LiepaASR][processRemote] ------------------ "<< std::endl;
      isInSpeech = false;
      
      //////////// For continuous recognition. Issue that it recognizes own words
      // recordWindowRemaining = 1; 
      // ps_start_utt(decoder);
      // isInRecognitionLock = false;
      // isUttStarted = true

      //// Single phrase recognition Mode. pause on recognition.
      pause();
      
  }

 
}

