// myservice.h
#include <qi/anyobject.hpp>
#include <qi/applicationsession.hpp>
#include <pocketsphinx.h>



class LiepaASR
{
public:
  // you can omit the session if you don't need it
  LiepaASR(qi::SessionPtr session);

  /**
   * testing if service works prints out some build information
   **/
  std::string version() const;
  /** 
   * initialize recognizer. It should be private
   **/
  std::string init() const;
  /**
   * Start listening of front microphone by subscribing event. Asynchronously system should start calling method processRemote(...). 
   * If this is first time when recognition is invoked, then initialize the sphinx. see method init() for more details. 
   * After recognition is over it should go to "stop" mode automatically. see method stop() for more details 
   **/
  std::string start() const;
  /**
   * Stop listening by ignoring microphone readings. This is need to wait till know robot generated noises are over(movement, generated speech etc)
   */
  std::string pause() const;
  /**
   * Turn off listening. this should be used then recognition activity is over or we need switch to another language model.
   */
  std::string shutdown() const;
  /**
   * Set grammar(as language model) from the  project. see attached samples for more info.
   */
  std::string setGrammarPath(std::string pGrammarPath) const;
  /**
   * Set dictionary(graphemes to phonemes for all words in grammar) from the project. see attached samples for more info.
   */
  std::string setDictionaryPath(std::string pDictionaryPath) const;
  /**
   * Method that does actual recognition as ALAudioDevice data stream was subscribed.
   **/
  void processRemote(int nbOfChannels, int samplesByChannel, qi::AnyValue altimestamp, qi::AnyValue buffer);

  /**
   * setters
   */
  std::string setVadThreshold(std::string pVadThreshold) const;
  std::string setVadPreSpeech(std::string pVadPreSpeech) const;
  std::string setVadStartSpeech(std::string pVadStartSpeech) const;
  std::string setVadPostSpeech(std::string pVadPostSpeech) const;
  std::string setSilenceProbability(std::string pSilenceProbability) const;

private:
  qi::SessionPtr _session;
  /**
   * pocket sphinx decoder
   */
  mutable ps_decoder_t *decoder; 
  /**
   * Window is one chunk of data that ALAudioDevice sends to processRemote. It is counter how much chunks should be skiped till recognition is started. 
   * Idea behind this is ignore all initial noises. Might be not needed
   **/
  mutable short recordWindowRemaining = 0;
  /**
   * Looks like sphinx is more comfortable with audio signals that are about ~0.4s. ALAudioDevice is sending about ~0.1s chunks. 
   * This counter keeps how much data is in buffer for pocketsphinx 
   */
  mutable short remainingSamples = 0;
  /**
   * Indicator that defines if pocket sphinx was loaded with grammar and dictionary 
   **/
  mutable bool isInitialized = false;
  /**
   * Indicator to track if someone changed grammar or dictionary, but sphinx was not reinitialized
   */
  mutable bool isModelChanged = false;
  /**
   * Indicator to store Voice Activity Detector state.
   */
  mutable bool isInSpeech = false;
  /**
   * Additional lock to make sure that sphinx are not disturbed during recognition. All audio data chunks will be ignored
   */
  mutable bool isInRecognitionLock = false;
  /**
   * Yet another lock to process recognition only when it was requested(see method start() for more details). 
   * If recognition is not started audio data chunks will be ignored.
   */ 
  mutable bool isUttStarted = false;
  /**
   * Count how many not recognized words it has. If number is high it could be issues with program(how pocket sphinx is used) or with human that interacts.
   */
  mutable short countSequentialFailures=0; 
  /**
   * Audio buffer keep pocket sphinx feeding with bigger data chunks. see attribute remainingSamples.
   */
  mutable std::vector<int16_t> audioBuffer;
  /**
   * Path where grammar file exists for a project
   **/
  mutable std::string grammarPath = "/home/nao/naoqi/lib/LiepaASRResources/tikrinimo.gram";
  /**
   * Path where dictionary file exists for a project
   **/
  mutable std::string dictionaryPath = "/home/nao/naoqi/lib/LiepaASRResources/tikrinimo.dict";

  mutable std::string vadThreshold = "3.0";
  mutable std::string vadPreSpeech = "20";
  mutable std::string vadStartSpeech = "10";
  mutable std::string vadPostSpeech = "50";
  mutable std::string silenceProbability = "0.005";
  

};

QI_REGISTER_MT_OBJECT(LiepaASR, version, start, pause, shutdown, processRemote, setGrammarPath, setDictionaryPath, setVadThreshold, setVadPreSpeech, setVadStartSpeech, setVadPostSpeech, setSilenceProbability); // QI_REGISTER_MT_OBJECT for multithread support. QI_REGISTER_OBJECT for single thread

