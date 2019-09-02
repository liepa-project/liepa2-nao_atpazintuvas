#include <qi/applicationsession.hpp>
#include <boost/shared_ptr.hpp>
#include "liepa_asr.h"

int main(int argc, char* argv[])
{
  qi::ApplicationSession app(argc, argv);
  app.startSession();
  qi::SessionPtr session = app.session();
  session->registerService("LiepaASR", qi::AnyObject(boost::make_shared<LiepaASR>(session)));
  app.run();
  return 0;
}
