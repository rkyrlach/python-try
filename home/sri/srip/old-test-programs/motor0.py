import can
import time
from can import Message
bus = can.interface.Bus('can0', bustype='socketcan_native')

#       open a can bus socket.... close it after move

#	// Convert tacho into inches
#	// wheel diameter = 59mm = 2.322835 inches
#	// wheel circumference = 7.2974 inches
#	// 1 tacho is 1/42nd of a revolution or 0.17375 inches

#	enum state { PLAN, MOVE, MOVE_LONG_UP, MOVE_LONG, MOVE_LONG_DN, FINAL, LOCK, HALT };
#	enum state curState = LOCK;
#	bool iNeedToHome = false;

#	// Calculate how many tachos equal one inch
#	const float iTach = 42.0 / wheel;
#	cout << "\tiTach: " << iTach << " (tachos) = (1 inch)" << endl;

#	cout << "\tCycle time: " << CYCLE << " (milliseconds)";
#	cout << "   " << ((float) CYCLE / 60000.0) << " (minutes)" << endl;

#	// Calculate how many eRPMs equal one tacho per cycle
#	const int32_t eTach = (7 * 60 * (1000 / CYCLE)) / 42;
#	cout << "\teTach: " << eTach << " (eRPMs) = (1 tacho per cycle)" << endl;

#	// Pre-calculte the number of tachos per cycle at full speed
#	const double tCycleFull = (double) CYCLE * (double) max_eRPM / 10000.0;
#	cout << "\ttCycleFull: " << tCycleFull << " Maximum (tachos per cycle)" << endl;

#	// Try to use these values and adjust if the ramp is too much
#	double tCycleTry = tCycleFull;
#	double eRPM_limit = (double) max_eRPM;

#	// Repeat calculation until acceleration is good
#	int32_t test;
#	bool too_fast = true;

#	// Which way?
#	bool forward = true;

#	// PID correction?
#	bool pid_engage = false;

#	// Distance variables
#	int32_t totalDistance     = 0;	// Total distance travelled for all movement
#	int32_t changeDistance    = 0;	// Distance between requested position and target
#	int32_t fudgeDistance     = 0;  // Distance past zero we need to insure home is really home
#	int32_t splitDistance     = 0;	// distance over 35 feet that we go full bore
#	int32_t startSplit	  = 0;  // tacho save for start high speed move
#	int32_t endSplit	  = 0;  // tacho save for begin slow down from high speed move
#	int32_t hsDistance	  = 0;  // home stopping distance for PID creep to home

#	// Obstantiate and initialize PID feedback control
#	std::shared_ptr<Wescott> pid;
#	pid = make_shared<Wescott>();

#	// Initialize things that are not going to change
#	pid->setLimits(iLimit);			// Anti wind-up limits
#	pid->setGains(pGain, iGain, dGain);	// P, I, D

#	// Obstantiate and initialize poly fit class
#	std::shared_ptr<PFit> poly;
#	poly = make_shared<PFit>();

#	// Actual position based on the VESC tacho value
#	// Unfortunately, we cannot use this value to compare
#	// against a calculated position because there will be
#	// values that tacho cannot actually be since it is an
#	// integer.  Instead we must make all comparisons in
#	// tacho units that are whole numbers.

#	// Position given over network is actually inches times ten
#	// so a 100 yard range from home position would be a value of:
#	// 3600 inches or 36000 of these units
#	// (well within an integer and still has good resolution)
#       _reqPos = (float) pos / 10.0;
#       cout << _reqPos << endl;

#	// Calculated position            at rest target and calcullated position are the same
#	int32_t calcPos = tacho.load();

#	// Target position for non-premptive motion
#	int32_t target = tacho.load();

#	// Prime PID before use
#	pid->updatePID(0, tacho.load());
#	bool pid_only = false;
#	int rtpause   = 0;
#	hsDistance = iTach * 18;    // slow down 18 inches before we hit

#	// Create a vector to store our list of eRPM values that follow
#	// the polynomial curve. and vectors for up and down (split)
#	std::vector<int32_t> rpm_list;
#	std::vector<int32_t> rpm_list_up;
#	std::vector<int32_t> rpm_list_dn;

#	// Define loop cycle time scheduling
#	std::chrono::system_clock::time_point tCycle =
#		std::chrono::system_clock::now() + std::chrono::milliseconds(CYCLE);

#	size_t i;

#   // Begin motion control processing
#   do {
#		switch (curState) {

#			case PLAN:		// Calculate how far we need to move and set variables

#				_reqTpos = (int32_t) ((_reqPos * 42.0) / wheel);

#				// For this move, snag the current requested position
#				// Don't look at _reqPos again until this move is complete.
#				target = _reqTpos;

#				_actTpos = tacho.load();	// Where are we?
#				// are we where we should be? if not add or subtract where we are from where we
#				// should be and add or subtract that from the next move... (coreects the creep problem)
#				forward = (target > _actTpos);	// Which way?
#				cout << "\tMoving " << (forward ? "forward" : "backward");
#				cout << " from: " << _actTpos << "   to: " << target << endl;

#				// find out if we are going home on this move and modify motion control if so
#				// complicated logic needed to home...
#				// if we have an 'h' command or a t,80 or less then home
#				// if we are more then 5 feet away plan to stop 5 feet short and creep in
#				// if we have a t,600 or less and direction is "in towards home" just creep
#				fudgeDistance = 0;   // normally fudge is zero
#				if ( (! forward) && (target <= 69)) {   // if we are going to within 1" of home then just go home 
#									//_actTpos < 60*iTach
#					iNeedToHome = true; // if we are going  home and we are less than 5 feet away only creep
#			                cout << " ********* We are headed home ************* " << endl;
#					fudgeDistance = 30000;  // ridiculous move past zero for testing fudge (should be 17 for 3")
#					}

#				// The mechanism behind this motion planner is as follows:
#				// First we look at the total distance we need to travel.
#				// Next we calculate how many cycles this would take at full speed.
#				// So multiply this number of cycles by 1.5.
#				// This count becomes our polynomial fit width.
#				// Then we set the max eRPM as the height of the polynomial fit.
#				// Now we can calculate the polynomial curve.
#				// With this curve, we can populate an array of nearly exact
#				// eRPM values to output for each cycle.  This will give us a
#				// nice smooth ramp-up/ramp-down without any non-linear jumps
#				// making it much more likely for our fine tune PID loop to
#				// track and compensate for the car, motor and motor control
#				// flucuations.

#				// We need to take the distance we need to travel
#				// and figure out how many steps are required. (add in fudge for home)

#				totalDistance = target - _actTpos;	// position desired - current POSITION (not window slop)
#                               splitDistance = 0;			// no leftovers
#				if (totalDistance < 0) { totalDistance = 0 - totalDistance; }
#				cout << "\tdistance: " << totalDistance << " (tachos)" << endl;
#				pid_only = false;

#				// if total distance is less than 30 inches then parabolic curve does not work
#				if (totalDistance <= 200) {  // setting it at 35 inches for safety margin
#					rpm_list.clear();
#					i = 0;
#				 	curState = MOVE;
#					pid_only = true;
#					cout << "###  MOVE-PID-ONLY 1st IF  ###" << endl;
#					break; }
#				// if total distance is between 34 inches and 60 inches then subtract 9 inches
#				if ((totalDistance > 200) & (totalDistance <= 345)) {
#					totalDistance = totalDistance - 54;
#					if (iNeedToHome) {totalDistance = totalDistance - hsDistance;}
#                                       else { totalDistance = totalDistance - 54; }
#					if ( totalDistance <= 200) {
#	                                        rpm_list.clear();
#        	                                i = 0;
#                	                        curState = MOVE;
#                        	                pid_only = true;
#	                              	        cout << "###  MOVE-PID-ONLY 2nd IF  ###" << endl;
#                                       	break; }
#					cout << "###  MOVE 35 inches to 5 feet  ###" << totalDistance << endl;
#					goto mkcurv;
#				}
#				// if total distance is between 60 inches and 120 inches then subtract 16 inches
#				if ((totalDistance > 345) & (totalDistance <= 690)) {
#					totalDistance = totalDistance - 54;
#                   			if (iNeedToHome) totalDistance = totalDistance - (hsDistance+54); //need home so PID last 5 feet
#					cout << "###  MOVE 5+ to 10 feet  ###" << endl;
#					goto mkcurv;
#				}
#				// if distance is > 10 feet and less than 15 feet then subtract 21 inches
#				if ((totalDistance > 690) & (totalDistance <= 1035)) {
#					totalDistance = totalDistance - 58;
#                   			if (iNeedToHome) totalDistance = totalDistance - (hsDistance+58); //so PID last 5 feet
#					cout << "###  MOVE 10+ to 15 feet  ###" << endl;
#					goto mkcurv;
#				}
#				// if distance is > 15 feet and less than 20 feet then subtract 28 inches
#				if ((totalDistance > 1035) & (totalDistance <= 1380)) {
#					totalDistance = totalDistance - 86;
#                   			if (iNeedToHome) totalDistance = totalDistance - (hsDistance+86); //so PID last 5 feet
#					cout << "###  MOVE 15+ to 20 feet  ###" << endl;
#					goto mkcurv;
#				}
#				// if distance is > 20 feet and less than 25 feet then subtract 36 inches
#				if ((totalDistance > 1380) & (totalDistance <= 1725)) {
#					totalDistance = totalDistance - 97;
#                   			if (iNeedToHome) totalDistance = totalDistance - (hsDistance+97); //so PID last 5 feet
#					cout << "###  MOVE 20+ to 25 feet  ###" << endl;
#					goto mkcurv;
#				}
#				// if distance is > 25 feet and less than 30 feet then subtract 48 inches
#				if ((totalDistance > 1725) & (totalDistance <= 2070)) {
#					totalDistance = totalDistance - 108;
#                    			if (iNeedToHome) totalDistance = totalDistance - (hsDistance+108); //so PID last 5 feet
#					cout << "###  MOVE 25+ to 30 feet  ###" << endl;
#					goto mkcurv;
#				}
#				// if distance is > 30 feet and less than 35 feet then subtract 52 inches
#				if ((totalDistance > 2070) & (totalDistance <= 2415)) {
#					totalDistance = totalDistance - 121;
#                   			if (iNeedToHome) totalDistance = totalDistance - (hsDistance+121); //so PID last 5 feet
#					cout << "###  MOVE 30+ to 35 feet  ###" << endl;
#					goto mkcurv;
#				}
#				// if distance is greater than 35 feet
#				splitDistance = 0;
#				if (totalDistance > 2415) {
#					totalDistance = totalDistance - 121;    // subtract our stopping distance allowance
#                                       if (iNeedToHome) totalDistance = totalDistance - (hsDistance+121); //so PID last 5 feet
#					if (totalDistance > 2415) {             // if we are still moving more than 35 feet
#						splitDistance = totalDistance - 2415;   // subtract 35 feet and calulate the split
#						startSplit       = 0;
#						endSplit 	 = 0;
#						cout << "###  LONG MOVE split: " << splitDistance << endl;
#						}
#					}
#				goto mkcurv;

#				// if distance is > 35 feet then set parabolic max speed to 2000 rpm
#				// if total distance is between 240 inches and 6000 inches then subtract 18 inches
#				// use parabolic ramp for 20 feet (10ft up to 2000) 2000 inbetween (10ft down) then
#				// pid the last 18 inches

#				// The maximum tachos per cycle at full speed = tCycleFull

#				// If the distance is short, we need to reduce the maximum speed,
#				// which in effect increases the number of cycles.  The idea here
#				// is to avoid a large jump in eRPMs for each cycle--under 100 eRPMs
#				// is a good limit.

#				// Try full speed first
#		mkcurv:		too_fast = true;
#				tCycleTry = tCycleFull;   tCycleFull= 84.000000      cycle = 25 milli-seconds
#				eRPM_limit = (double) max_eRPM;  eRPM_limit = 33600   max eRPM=33600
#				if ( splitDistance > 0) {totalDistance = 2415;} //only use 35 feet for the curve calcs
#				do {
#					// How many cycles are required
#					numCycles = totalDistance / tCycleTry;   (600" * 5.755486 t/in) / 84 =  41.1 cycles

#					numCycles *= 1.5;	// Our magic factor       42 * 1.5 = 61.6
#					cout << "\tnumCycles: " << numCycles << endl;

#					// Enter the necessary data for computing a curve fit
#					poly->setPeek((double) eRPM_limit);
#					poly->setWidth((double) numCycles);

#					poly->calc();		// Calculate the curve

#					cout << "\ty = (" << poly->getX2() << ") x^2 + (" << poly->getX1() << ") x" << endl;

#					// Look at the first ramp point
#					test = (int32_t) (poly->getX1() + poly->getX2());

#					// We good?
#					if (test < MAX_ACCEL) { too_fast = false; }

#					// Guess not.  Reduce max eRPM by 25%
#					eRPM_limit *= 0.75;
#					tCycleTry = (double) CYCLE * eRPM_limit / 10000.0;

#				} while (too_fast);		// Recalc if not within acceptible limits

#				// Now load the rpm_list with values calculated from the curve fit
#				rpm_list.clear();
#				for (i = 0; i <= numCycles; i++) {
#					rpm_list.push_back((int32_t) ((double) i * poly->getX1() + (double) (i * i) * poly->getX2()));
#					}
#				curState = MOVE;
#				// cout << "###  MOVE  ###" << endl;
#				if (splitDistance > 0) {
#					curState = MOVE_LONG_UP;
#					rpm_list_up.clear();
#					numCyclesDiv2 = numCycles/2;    // first half the curve for up and second half for down
#					for (i = 0; i <= numCyclesDiv2; i++) {
#						rpm_list_up.push_back((int32_t) ((double) i * poly->getX1() + (double) (i * i) * poly->getX2()));
#						}
#					rpm_list_dn.clear();
#					for (i = numCyclesDiv2 + 1; i <= numCycles; i++) {
#						rpm_list_dn.push_back((int32_t) ((double) i * poly->getX1() + (double) (i * i) * poly->getX2()));
#						}
#				}

#				if (iNeedToHome) { totalDistance = totalDistance + fudgeDistance;
#						   cout << "\tFudge Distance = " << totalDistance << endl; }
#				i = 0;		// Start at the beginning
#				break;

#			case MOVE:	// Begin moving the car by reading eRPM ard sending it to the VESC.
#					// Are we done with parabolic curve yet?
#				if (pid_only) {
#					pid_engage = true;                      // Engage PID control loop
#					pid->clearState();
#					pid->updatePID(0, tacho.load());        // Prime PID before use
#					curState = FINAL;
#					pid_only = false;
#					cout << "###  FINAL PID ONLY  ###" << endl;
#					cout << "\tFinal Position: " << tacho.load();
#					cout << "   Target Position: " << target << endl;
#					rtpause = 0;
#					break;
#					}

#				if (i >= rpm_list.size()) {   				// kick PID in before curve finishes
#					pid_engage = true;                      // Engage PID control loop
#					pid->clearState();
#					pid->updatePID(0, tacho.load());        // Prime PID before use
#					curState = FINAL;
#					cout << "###  FINAL CURVE ###" << endl;
#					cout << "\tFinal Position: " << tacho.load();
#					cout << "   Target Position: " << target << endl;
#					rtpause = 0;
#				 	break;
#					}
#				// Run through the vector
#				eRPM = rpm_list[i];
#				if (! forward) { eRPM = 0 - eRPM; }
#				//cout << "eRPM Set: " << rpm_list[i] << " I: " << i << endl;
#				i++;		// Next.
#				break;

#			// if we are going more than 35 feet we split the curve and eat up the rail
#			case MOVE_LONG_UP:   //ramp up to high speed
#				if (i >= numCyclesDiv2) {
#					curState = MOVE_LONG;  //up to speed so now maintain it
#					startSplit = tacho.load();
#					cout << "\tRamp up finished at: " << startSplit << endl;
#					break;
#				}
#				// Run through the ramp up vector
#				eRPM = rpm_list_up[i];
#				if (! forward) { eRPM = 0 - eRPM; }
#				cout << "eRPM ramp up: " << rpm_list_up[i] << endl;
#               		i++;
#				break;
#			case MOVE_LONG:       //keep going fast
#				// Lets see how things stand every 25 milliseconds
#				endSplit = startSplit - tacho.load();
#				if (endSplit < 0) { endSplit = 0 - endSplit; }
#				if (endSplit >= splitDistance) {     // are we in slowdown range yet?
#					curState = MOVE_LONG_DN;
#					i = 0;
#					cout << "\tHold speed finished at tacho: "  << tacho.load() << endl;
#					break;
#					}
#				// else hold max speed during fast travel mode
#				eRPM = rpm_list_up[numCyclesDiv2];
#				if (! forward ) { eRPM = 0 - eRPM; }
#				break;
#			case MOVE_LONG_DN:     //ramp back down to final PID range
#				if (i == numCyclesDiv2) {      // we are slowed down now so final PID into target
#					pid_engage = true;                      // Engage PID control loop
#					pid->clearState();
#					pid->updatePID(0, tacho.load());	// Prime PID before use
#					curState = FINAL;
#					cout << " ramp down finished at position: " <<  tacho.load() << endl;
#				        //std::this_thread::sleep_for(std::chrono::milliseconds(100));  
#					//wait for current spike to go away
#					rtpause = 0;
#					break;
#					}
#				// Run through the ramp down vector
#				eRPM = rpm_list_dn[i];
#				if (! forward) { eRPM = 0 - eRPM; }
#				cout << "eRPM ramp down: " << rpm_list_dn[i] << " list index = " << i <<  endl;
#				i++;
#				break;

#			// We stay here in the final state until the target position has been
#			// reached and the motor is stopped.
#			case FINAL:
#				// Lets see how things stand
#				totalDistance = target - tacho.load();
#				if (totalDistance < 0) { totalDistance = 0 - totalDistance; }
#			    if (totalDistance <= 10) cout << "\tApproching destination " <<  totalDistance << endl;
#				// Are we where we want to be +/- a small amount?
#				if (iNeedToHome) {
#		                    // motor current is > 5 amps then kill power and go to lock
#                		    // I.E. is the motor stalled due to an obstruction or being "home"
#				    float cla = 0.0;
#				    //if ( abs(current.load()) > 87 ) break;     if (abs(current.load()) < 110) 
#				    for (int ri = 0; ri <= 799; ri++) { cla += abs(current.load());}
#				    cla = cla / 8000.0;   //div by factor of ten ore to shift the decimal point to actual amps
#                                   cout <<  "\tDebug current I = " << cla << endl;
#				    if((rtpause >= 7) && (cla >= 8.7)) {   // how many amps is locked?
#                        		curState = HALT;
#                        		// tell can bus to reset tacho to 0 here (not currently implemented)
#					// prolly don't want to do this if it is jammed on a shell
#					cout << "\t###  HOME LOCK  ###" << " tacho position now = " << tacho.load() << endl;
#					cout << "\tRPM =: " << rpm.load() << " current =: " << float(current.load()/10.0) << " duty =: " << duty.load() << endl;
#					cout << "\tAmp hours =: " << amp_hours.load() << " amp hours charged =: " << amp_hours_charged.load() << endl;
#					cout << "\tWatt hours =: " << watt_hours.load() << " watt hours charged =: " << watt_hours_charged.load() << endl;
#					cout << "\tMotor temperature =: " << temp_motor.load() << " Voltage in =: " << float(v_in.load())/10.0 << endl;
#					iNeedToHome = false; //we have now handled the "home" command so turn off our need..
#					}
#				    }
#				if ((! iNeedToHome) && (totalDistance <= TOLERANCE + 3)) { //we are not going home on this move
#					if (abs(rpm.load()) <= 1.0) {
#						curState = LOCK;
#						cout << "\t###  LOCK  ###" << " tacho position now = " << tacho.load() << endl;
#						cout << "\tRPM =: " << rpm.load() << " current =: " << float(current.load()/10.0) << " duty =: " << duty.load() << endl;
#						cout << "\tAmp hours =: " << amp_hours.load() << " amp hours charged =: " << amp_hours_charged.load() << endl;
#						cout << "\tWatt hours =: " << watt_hours.load() << " watt hours charged =: " << watt_hours_charged.load() << endl;
#						cout << "\tMotor temperature =: " << temp_motor.load() << " Voltage in =: " << float(v_in.load())/10.0 << endl;
#					}
#				}
#				// We should be at the target position right now.  if we are going home make a fudge
#				calcPos = target-fudgeDistance;    //we must rely on the endstop and motor current to lock into home
#				break;
#			// To be in this state, we must ensure the car is not moving and
#			// that we are in fact at the requested target position.
#			// Only here do we again look for a new requested position.
#			case LOCK:	// Lock the motor at this position and wait

#				_reqTpos = (int32_t) ((_reqPos * 42.0) / wheel);

#				// Need to look for any significant changes
#				changeDistance = _reqTpos - target;
#				if (changeDistance <= 0) { changeDistance = 0 - changeDistance; }

#				if (changeDistance > 0) {}
#				// Is this a wiggle or a real move?
#				if (changeDistance >= TOLERANCE+3) {
#					curState = PLAN;		// Plan a new move
#					pid_engage = false;		// Disengage PID control loop
#					cout << "###  PLAN  ###" << endl;
#				}
#				// Otherwise we stay in this state and let the PID keep the motor locked.
#				// We should be at the target position right now.
#				calcPos = target;
#				break;

#			// The endstop sensor has been triggered.
#			// We can only move in the opposite direction that got us here.
#			// So lets set our target position slightly away from marker and attempt to lock.
#			case HALT:

#				if (forward) {		// were we going forward when we hit the end stop?
#					target = _high_limit - TOLERANCE;
#					cout << "###  LOCK-RAIL-END  ###" << endl;
#				     }
#				else {                  // were we going home when we hit the end stop
#					target = tacho.load();                  // was  _low_limit + TOLERANCE;
#					cout << "###  LOCK-HOME  ###" << endl;
#					// Since we hit a limit and could not actually get to the
#					// requested position, we need to change the requested position
#					// so the lock routine doesn't immediately jump to planning a
#					// new move.
#					_reqPos = (float) target * wheel / 42.0;
#					cout << "\tNew home target = " << target << " new requested pos. = " << _reqPos << endl;
#					cout << "\tHalted offset.load() = " << toffset.load() << " target = " << target << endl;
#					toffset.store(toffset.load() + target);  // change offset value by new position
#					tacho.store(0);                          // set new tacho "zero"
#					cout << "\tNew offset.load() = " << toffset.load() << " position = " << tacho.load() << endl;
#					target = 0;    // we are home
#					_reqPos = 0;   // we are where we are required to be
#                                	cout << "\tNew home target = " << target << " new requested pos. = " << _reqPos << endl;
#				     }
#                               curState = LOCK;
#                               eRPM = 0;      			// we have motor stop
#				pid_engage = false;   		// turn off PID
#				halt.store(false);		// Clear error condition
#				calcPos = target;		// target achieved
#				break;
#		}

#		// Getting an actual position is relatively easy.  A calculated position
#		// is a bit trickier.  What we need to do at each interval is to
#		// calculate a displacement that can be accumulated with all previous
#		// displacements in order to know the true expected position.
#		// A displacement can be calculated by averaging the previous cycle
#		// velocity with the current cycle velocity and multiplying by the
#		// cycle time to get a distance--a displacement distance for that
#		// cycle.  To make this work we need to be able to easily calculate
#		// a velocity from the eRPM, retain the last cycle's velocity and
#		// accumulate displacements throughout the movement.  The best part
#		// of this method is that we do not need to keep track of time at all.


#		//cout << "Calculated position: " << calcPos << "   Actual position: " << tacho.load();
#		//cout << "   Clean eRPM: " << eRPM << "   PID eRPM: " << eRPMrun << endl;

#		// Test for emergency stop and set limits based on direction of travel
#		if (halt.load()) {
#			curState = HALT;		// Change state
#			cout << "###  HALT  ###" << endl;
#			eRPM = 0;			// Stop the motor
#			pid_engage = false;		// Disengage PID control loop

#			if (forward) {
#				_high_limit = tacho.load();
#				cout << "\tHigh limit hit at tacho position: " << _high_limit << endl;
#			}
#			else {
#				_low_limit = tacho.load();
#				cout << "\tLow limit hit at tacho position: " << _low_limit << endl;
#			}
#		}

#		// We don't want the PID controller interferring with the
#		// calculated values, so we use an intermediate variable here.
#		eRPMrun = eRPM;

#		if (pid_engage) { //  updatePID( error , position) ie  error=(calcPos-curpos) , position 
#			eRPMrun += pid->updatePID(calcPos - tacho.load(), tacho.load());
#		}

#		// Extract integer data and place in frame
#		frame.data[0] = (unsigned char) ((eRPMrun & 0xff000000) >> 24);
#		frame.data[1] = (unsigned char) ((eRPMrun & 0x00ff0000) >> 16);
#		frame.data[2] = (unsigned char) ((eRPMrun & 0x0000ff00) >>  8);
#		frame.data[3] = (unsigned char)  (eRPMrun & 0x000000ff);

#		sent_bytes = write(s, &frame, required_mtu);	// Send eRPM setting to CANbus
#   		if (sent_bytes != required_mtu) {
#			cerr << "CAN write error" << endl;
#   	    		_done = true;
#    			}
#		frame.can_id ^= 0x00000003;			// XOR bit 1 & bit 0 -- toggle between IDs 01 & 02
#		write(s, &frame, required_mtu);		// Send eRPM setting to CANbus with other ID

#		// Delay long enough to make up up difference between the time we
#		// consumed and the cycle time we want to run at.
#	        std::this_thread::sleep_until(tCycle);

#		// Schedule next cycle in advance
#		// The time through the loop may change, but each cycle will
#		// be scheduled on CYCLE intervals regardless, making the average
#		// cycle time very accurate.
#		rtpause += 1;
#		tCycle += std::chrono::milliseconds(CYCLE);

#    } while (! _done);


print("\033[44;1H                                                          ")
print("\033[45;1H                                                          ")
cnt = 0
def msg(nn):
    switcher={
       2305:'VESC Status message 1 ', # bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00')
       3585:'VESC Status message 2 ', # bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00')
       3841:'VESC Status message 3 ', # bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00')
       4097:'VESC Status message 4 ', # bytearray(b'\x01\x1a\xfc\x99\x00\x00\x18\xf5')
       6913:'VESC Status message 5 '} # bytearray(b'\x00\x00\x00\x96\x00\xef\x00\x00')
    return switcher.get(nn,"Invalid can message")
while cnt <= 50:
      message1 = bus.recv()
      #print('msg from can = ', message.data)
      num = int(message1.arbitration_id)
      msgn = msg(num)
      if(msgn.find('5') != -1):
         a=message1.data[0]; b=message1.data[1]; c=message1.data[2]; d=message1.data[3]
         e=message1.data[4]; f=message1.data[5]
         tacho = (d + (c*256) + (b*65536) + (a*16777216))
         if (a==255): tacho = tacho-4294967296
         vin = (f + (e*256))/10.0
         packet = Message(arbitration_id=1, data=[0, 0, cnt, 0])
         bus.send(packet)
         print("data = ", packet, " \n")
         cnt = cnt + 1
         print ("\033[44;1Htacho = ", tacho, " Vin = ", vin)
#      time.sleep(0.025)
while cnt != 0:
      message1 = bus.recv()
      #print('msg from can = ', message.data)
      num = int(message1.arbitration_id)
      msgn = msg(num)
      if(msgn.find('5') != -1):
         a=message1.data[0]; b=message1.data[1]; c=message1.data[2]; d=message1.data[3]
         e=message1.data[4]; f=message1.data[5]
         tacho = (d + (c*256) + (b*65536) + (a*16777216))
         if (a==255): tacho = tacho-4294967296
         vin = (f + (e*256))/10.0
         packet = Message(arbitration_id=1, data=[0, 0, cnt, 0])
         bus.send(packet)
         print("data = ", packet, " \n")
         cnt = cnt - 1
         print ("\033[44;1Htacho = ", tacho, " Vin = ", vin)
#      time.sleep(0.025)
packet = Message(arbitration_id=1, data=[0, 0, 0, 0, 0])
packet = Message(arbitration_id=1, data=[0, 0, cnt, 0])
exit()

#// VESC Status message #1
#std::atomic<int32_t> rpm;
#std::atomic<int16_t> current;
#std::atomic<int16_t> duty;


#// VESC Status message #2
#std::atomic<int32_t> amp_hours;
#std::atomic<int32_t> amp_hours_charged;

#// VESC Status message #3
#std::atomic<int32_t> watt_hours;
#std::atomic<int32_t> watt_hours_charged;

#// VESC Status message #4
#std::atomic<int16_t> temp_fet;
#std::atomic<int16_t> temp_motor;
#std::atomic<int16_t> current_in;
#std::atomic<int16_t> pid_pos_now;

#// VESC Status message #5
#std::atomic<int32_t> tacho;      // VESC motor position
#std::atomic<int16_t> v_in;

