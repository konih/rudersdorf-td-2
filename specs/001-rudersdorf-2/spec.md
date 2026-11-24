# Feature Specification: Rudersdorf 2 · Das Labyrinth

**Feature Branch**: `001-rudersdorf-2`
**Created**: 2026-11-24
**Status**: Draft
**Input**: The owner's request: version 2 of the learning game Rudersdorf, built with his son
(the learner, called Luki in the game). Much better performance and graphics, more options, higher
difficulty, different enemies, free placement on a grid, castable magic with upgrades, an
upgradable church that grows into a gothic cathedral with a healing or magic effect, and a
well-developed village with several varied upgrade options. It stays a learning game: a complete
reference version plus exercises for the learner, with a better learning experience than version 1.

## Background: what version 1 was

Version 1 is a Tkinter game with one fixed path, nine fixed build spots, ten waves, four towers,
five enemies and seventeen test-driven missions in two files. The learner has solved sixteen of
them. He knows classes, `__init__`, inheritance with `super()`, lists, dictionaries, loops,
conditions, simple type hints and sorting with a `lambda` key. His code shows what to teach next:
the same distance formula copied three times, booleans returned through paired `if` statements,
and an attribute typo that nothing caught. Version 1 stops the action whenever an unsolved mission
is reached, redraws everything every frame, and has no sound.

Version 2 is a new game in a new repository. It does not import or migrate version 1.

## User Scenarios & Testing *(mandatory)*

Two kinds of people use this product. The **player** plays the finished game (the reference, or
the learner's own build once missions are solved). The **learner** writes Python in `werkstatt/`
and watches the game improve. The **parent** accompanies the learner.

### User Story 1 - Defend the village on a free grid (Priority: P1)

The player sees a map made of square cells: meadow, rock, water, swamp, hills, one or more orc
gates and the village gate. Between and during waves the player places towers and palisades on
any free buildable cell. Enemies walk the shortest route from their gate to the village gate and
re-route immediately when the player builds, so the player shapes a labyrinth. A placement that
would cut the last route is refused with an explanation. Towers shoot enemies in range according
to a targeting rule the player can choose per tower. Kills pay gold; enemies that reach the gate
damage the village. The player wins by surviving the last wave and loses when the village has no
life left.

**Why this priority**: this is the game. Everything else builds on the grid, the routing and the
combat loop.

**Independent Test**: start the reference, place towers so the route bends, start waves, and see
enemies follow the bent route, die to towers, and the match end in victory or defeat.

**Acceptance Scenarios**:

1. **Given** an empty map, **When** the player places a tower on a meadow cell on the current
   route, **Then** the tower appears, its price is deducted, and every walking enemy from then on
   takes the new shortest route.
2. **Given** a wall of towers with one gap, **When** the player tries to build in the gap,
   **Then** nothing is built, nothing is paid, and a message says the orcs need a way through.
3. **Given** an enemy standing on or walking into a cell, **When** the player tries to build on
   that cell, **Then** the placement is refused.
4. **Given** a tower with enemies in range, **When** its reload time has passed, **Then** it hits
   the enemy its targeting rule selects, and the hit is visible.
5. **Given** a selected tower, **When** the player changes its targeting rule, upgrades it or
   sells it, **Then** the rule is used from the next shot, the upgrade changes its values and
   costs gold, and selling removes it, refunds part of what was spent and re-opens the cell.
6. **Given** the last wave is cleared with village life above zero, **Then** the match ends in
   victory; **given** village life reaches zero, **Then** it ends in defeat. Both screens show
   wave reached, enemies defeated and gold earned (`Spiel.statistik()`), and offer a new match.

---

### User Story 2 - Learn by upgrading a game that always runs (Priority: P1)

The learner opens the repository, installs one package and starts the game. It runs at once,
although no mission is solved: orcs walk straight through everything like ghosts, towers pick
targets at random, the village offers only its first level. Each of these weaknesses carries a
label on screen naming the mission that fixes it. The learner picks a mission from one of several
independent tracks, reads its document, runs its test, writes code in `werkstatt/`, and after
pressing one key in the running game sees the change: now the orcs walk around his towers.

**Why this priority**: the product is a learning game. A fine game that cannot be learned with
has failed, and version 1's biggest weakness was that unsolved missions stopped the fun.

**Independent Test**: with an untouched `werkstatt/`, start the game, play three waves without an
error, read the labels of the active stand-ins; solve one mission by copying its reference
function into `werkstatt/`, reload, and see that label disappear and the behaviour change.

**Acceptance Scenarios**:

1. **Given** an untouched workshop, **When** the learner starts the game and plays three waves,
   **Then** no error appears and the screen lists which stand-ins are active and which mission
   replaces each.
2. **Given** a mission's functions are implemented correctly, **When** the learner reloads the
   workshop from inside the game, **Then** a new match starts on the same map and difficulty, the
   stand-in label for that capability is gone and the real behaviour is in effect.
3. **Given** learner code that raises an ordinary Python error, **When** the game calls it,
   **Then** the match pauses and a panel names the workshop file, the line, the error type and
   message and the mission concerned; after a fix and a reload the game continues.
4. **Given** any mission number, **When** the learner runs the test runner for it, **Then** each
   test reports in German whether it passed, what was expected, what happened, and one hint.
5. **Given** the learner runs the test runner without arguments, **Then** a mission board lists
   every mission by track with its state (solved, in progress, open) and suggests a next mission.
6. **Given** the explicit reference switch, **Then** the same game and the same tests run against
   the reference; without the switch the reference is never used.

---

### User Story 3 - Grow the village and its cathedral (Priority: P2)

Beside the battlefield lies Rudersdorf. Between waves the player spends gold and stone on village
buildings, each with several levels and its own lasting effect: a smithy that strengthens towers
and unlocks master upgrades, a market for income and interest, a quarry for stone, houses for
population, a town wall for village life and armour, a masons' lodge that makes building cheaper,
a library for magic research, and the church. The church grows through five visibly different
stages from a wooden chapel to a gothic cathedral with flying buttresses, a rose window and twin
towers. It heals the village after each wave, produces mana, and its bells stun the attackers at
intervals once it is a cathedral. Higher levels need other buildings first, so the player plans a
route through the tree, and the game can show that route.

**Why this priority**: the owner asked for village development to be really well developed, and
the learner loves gothic cathedrals. It is the long-term goal of a match.

**Independent Test**: in the reference, play several waves, raise at least three different
buildings, see each effect in play and on the info panel, and raise the church through all five
stages with a different picture at each.

**Acceptance Scenarios**:

1. **Given** enough resources and met requirements, **When** the player raises a village building,
   **Then** the cost is deducted, the building's picture changes, and its effect applies from then on.
2. **Given** an unmet requirement, **When** the player selects that upgrade, **Then** it cannot be
   bought and the panel lists what is missing and the full build order that leads there.
3. **Given** a church of stage 1 or higher, **When** a wave ends, **Then** the village regains
   life up to its maximum; **and** during waves mana rises over time up to its maximum.
4. **Given** a church of stage 4 or higher, **When** its bell interval elapses during a wave,
   **Then** every enemy on the map is stunned briefly and the bells are seen and heard.
5. **Given** each of the five church stages, **Then** the church is drawn differently and
   recognisably larger and more gothic than the stage before.
6. **Given** a smithy, market, quarry, wall, lodge, library or houses at any level, **Then** the
   stated effect is measurable in play (damage, income, stone, village life, prices, spell levels,
   population).

---

### User Story 4 - Cast magic (Priority: P2)

Once the village has a church, the player has mana and a spell bar. The player selects a spell and
clicks the map to cast it: a fireball that burns a group, an ice storm that slows an area, a
lightning strike on one strong enemy, a blessing that heals the village, and the great bell that
stuns everything. Each spell costs mana and has a cooldown. Spells are unlocked by church stages
and improved in the library through several levels.

**Why this priority**: explicitly requested, and it gives the player something to do during a
wave besides watching.

**Independent Test**: in the reference with a church, cast each unlocked spell during a wave and
see its effect, its mana cost and its cooldown; upgrade one spell and see the stronger effect.

**Acceptance Scenarios**:

1. **Given** enough mana and a ready spell, **When** the player casts it at a point, **Then**
   mana drops by its cost, its effect is applied to the enemies or the village as described, a
   visible effect plays, and the spell cannot be cast again until its cooldown has passed.
2. **Given** too little mana or a running cooldown, **When** the player tries to cast, **Then**
   nothing happens except a short message saying why.
3. **Given** a library of sufficient level, **When** the player buys a spell upgrade, **Then** the
   spell's next cast is stronger as described and the upgrade is listed.
4. **Given** a church stage that unlocks a spell, **Then** the spell appears in the bar; spells not
   yet unlocked are shown locked with the requirement.

---

### User Story 5 - Face a varied, much harder horde (Priority: P2)

A campaign has twenty waves. The horde now has enemies that change how the player must build:
fast wolf riders, heavy ogres, armoured shield orcs, regenerating trolls, harpies that fly over
the labyrinth, shamans that heal others, slimes that split when killed, ghosts that shrug off
arrows, breakers that walk straight at the village and smash what stands in their way, and the
orc king, a boss who summons orcs. Damage has types, and enemies resist some of them. The player
chooses a map and one of four difficulty levels before the match, and may continue in an endless
mode after victory. Towers gain a third-level choice between two master upgrades.

**Why this priority**: explicitly requested (higher difficulty, different enemies, more options).

**Independent Test**: play the reference on normal difficulty; see each enemy kind appear and
behave as described; lose with a single-tower-type defence that wins easily on the easy level.

**Acceptance Scenarios**:

1. **Given** each enemy kind, **Then** it behaves as its description says: harpies ignore the
   labyrinth and cannot be hit by cannons; shamans heal others nearby; slimes leave smaller slimes;
   trolls regenerate unless burning; breakers destroy buildings in their straight path; the orc
   king summons orcs and ignores stuns.
2. **Given** an enemy with a resistance to a damage type, **When** it is hit with that type,
   **Then** it loses correspondingly less life, and the hit is shown as weak.
3. **Given** the four difficulty levels, **Then** harder levels give enemies more life, bigger
   waves, less starting gold and less village life, and the menu says so.
4. **Given** waves 10 and 20, **Then** a boss appears and is announced.
5. **Given** a map with two orc gates, **Then** enemies arrive from both and each takes its own
   shortest route.
6. **Given** a tower at level 2 and a smithy of the required level, **When** the player upgrades
   it, **Then** the player chooses one of two master upgrades with different strengths.
7. **Given** victory in the campaign, **When** the player chooses to continue, **Then** further
   waves of growing strength follow without end and the best wave is recorded.

---

### User Story 6 - See and hear a lively, smooth game (Priority: P2)

The game looks hand-made and alive: varied terrain, animated water, enemies that bob and face
their direction, towers that turn towards their target, flying projectiles, sparks, frost, poison,
fire, coins, spell effects, a village with people and a cathedral whose windows glow. There are
simple sounds that can be switched off. The game runs smoothly even with a large horde, in a
resizable window or full screen, at one, two or four times speed.

**Why this priority**: explicitly requested (better performance, better graphics).

**Independent Test**: play a late wave in the reference at four times speed with the frame-rate
display on and see it stay smooth; look at the screenshots the preview tool produces.

**Acceptance Scenarios**:

1. **Given** 200 enemies and 50 towers on the map, **Then** the game still shows at least 60
   frames per second on the owner's computer, and the frame-rate overlay shows it.
2. **Given** a hit, a kill, a spell or a building, **Then** a matching visual effect plays and,
   with sound on, a matching sound.
3. **Given** the options menu, **When** the player switches sound off, changes speed or toggles
   full screen, **Then** the choice applies at once and is remembered for the next start.
4. **Given** a computer without a sound device, **Then** the game runs silently without an error.
5. **Given** the overlay keys, **Then** the player can show the route distances on every cell, the
   range of every tower, and the frame rate with simulation time.

---

### User Story 7 - Work like a programmer in the workshop (Priority: P3)

Beyond game rules, the learner practises the craft: hunting prepared bugs with the help of error
messages, cleaning up working but ugly code while tests stay green, writing his own tests that
must catch prepared mistakes, saving and loading a match with validation, analysing many
simulated matches in a balance laboratory, and finally writing a bot that plays the game by
itself and can be switched on in the real game.

**Why this priority**: it is the largest step in learning, but it needs the finished game.

**Independent Test**: run the laboratory against the reference bot and read its table; run the
own-tests mission with the reference tests and see every prepared mistake caught.

**Acceptance Scenarios**:

1. **Given** the bug-hunt file as shipped, **Then** its tests fail with ordinary Python errors or
   wrong results; after the fixes described in the reference they pass.
2. **Given** the clean-up file as shipped, **Then** its behaviour tests pass and its tidiness
   checks fail; in the reference both pass.
3. **Given** the learner's own tests, **When** the checker runs them against a correct subject and
   against each prepared faulty one, **Then** it reports which faults his tests catch, and the
   mission is solved when they pass on the correct one and fail on every faulty one.
4. **Given** a match in the build phase, **When** the player saves and later loads, **Then** the
   match continues with the same map, difficulty, wave, resources, buildings, tower levels,
   targeting rules, village levels and spell levels; a damaged file is refused with a reason and
   the running match stays untouched.
5. **Given** the laboratory command with a number of matches, **Then** it plays them without a
   window, much faster than real time, and prints wins, best and average wave per difficulty.
6. **Given** the learner's bot, **When** the player switches autopilot on in the game, **Then**
   the bot builds and starts waves by itself, and the player can switch it off again.

---

### User Story 8 - Find one's way as learner and parent (Priority: P3)

Every mission has a German document with a story, what is practised, the exact contract, worked
examples, a done-when line, graded hints that stay hidden until opened, what will change in the
game, and a thinking question. Help fades from track to track: early missions give a contract and
examples, later ones mainly tests, the last ones a goal. A parents' page explains the idea and how
to help without solving; an extension guide shows how to add towers, enemies, spells, buildings
and maps; a page of open challenges suggests what to invent next.

**Why this priority**: needed for the learner to work alone, but written last because it
describes the finished thing.

**Independent Test**: pick three missions at random; each document alone is enough to solve its
mission against the tests.

**Acceptance Scenarios**:

1. **Given** any mission, **Then** its document exists, contains every part listed above, and
   every command, file, function and key it names exists.
2. **Given** the start page, **Then** a newcomer can install, start, test one mission and find
   the reference by following it step by step.

---

### Edge Cases

- A map file with rows of different length, no village gate, two village gates, no orc gate, or an
  unknown character is refused with a German message naming the problem; the built-in map is used.
- The player builds while enemies are mid-step: each enemy finishes its step, then follows the new
  route. No enemy is ever enclosed: a placement that would cut off any walking enemy is refused.
- A breaker destroys a tower: the cell becomes free and routes are recalculated.
- A slime dies on the village gate cell, or a summoned orc appears next to the gate: they behave
  like any enemy at that position.
- Flying enemies are over a cell the player builds on: allowed; they are not on the ground.
- A wave is started while the previous one still runs (early call): not allowed; the key does
  nothing until the wave is over. Speed and pause still work.
- A spell is cast at a point with no enemy in reach: mana and cooldown are still spent; the
  message says nothing was hit.
- The learner's targeting function returns something that is not one of the candidates, or his
  bot returns nonsense actions: treated as a learner error (pause and panel), respectively ignored
  and counted (bot), never a crash.
- The window loses focus or is resized: the match pauses on focus loss; drawing scales with the
  window and keeps its proportions.
- A save file from another map, an unknown tower kind or a level above the maximum: refused.
- Resources never go below zero; village life never exceeds its maximum; mana never exceeds its
  maximum.

## Requirements *(mandatory)*

### Functional Requirements

**Battlefield and building**

- **FR-001**: The battlefield MUST be a grid of 24 by 16 cells whose rightmost six columns are
  village ground. Terrain kinds: meadow (walkable, buildable), rock (neither), water (neither;
  flyers cross), swamp (walkable at half speed, not buildable), hill (walkable, buildable, towers
  on it gain 25 % range), orc gate (walkable, not buildable), village gate (walkable, not
  buildable), village ground (neither).
- **FR-002**: Maps MUST be plain text files, one character per cell, readable and editable by the
  learner. At least four maps MUST ship, at least one with two orc gates and one wide open.
- **FR-003**: The player MUST be able to place any affordable building on any free buildable cell
  in the build phase and during a wave. Buildings block walking enemies.
- **FR-004**: A placement MUST be refused when the cell is not buildable or occupied, when a
  walking enemy is on or heading into the cell, or when afterwards any orc gate or any walking
  enemy would have no route to the village gate. A refusal costs nothing and states its reason.
- **FR-005**: Walking enemies MUST follow a shortest route by number of cells from their position
  to the village gate, moving between horizontally or vertically adjacent cells, and MUST adopt a
  changed route at their next cell.
- **FR-006**: Buildings MUST include at least five tower kinds with distinct roles (fast single
  target; area damage against ground; slowing; damage over time; chain lightning), a cheap
  palisade that only blocks, and all MUST be sellable for a stated share of the amount spent.
- **FR-007**: Each tower MUST have three levels. The third level MUST be a choice between two
  master upgrades and MUST require the smithy level stated in the data.
- **FR-008**: Each tower MUST have a targeting rule chosen by the player from a list containing at
  least first, last, strongest, weakest and nearest, plus every rule the learner has registered.

**Enemies, damage, waves**

- **FR-009**: There MUST be at least ten enemy kinds, including: a basic orc, a fast one, a heavy
  one, an armoured one, a regenerating one, a flying one, a healer, a splitter, a ghost with
  strong resistances, a breaker that attacks buildings, and a summoning boss.
- **FR-010**: Damage MUST have a type (pierce, impact, magic, poison, fire). Every enemy kind MUST
  define a multiplier per type, default one.
- **FR-011**: Lasting effects (slow, poison, burn, stun) MUST be independent objects attached to
  an enemy; a new effect of a kind already present replaces it if it lasts at least as long,
  never stacks. Burning MUST stop regeneration. Bosses MUST ignore stuns.
- **FR-012**: A campaign MUST have twenty waves, with bosses at waves 10 and 20. Ordinary waves
  MUST be generated from a wave budget and the enemy kinds unlocked at that wave, reproducibly
  from the match seed. After victory the player MUST be able to continue endlessly.
- **FR-013**: The player MUST choose map and difficulty (four levels) before a match. Difficulty
  MUST scale enemy life, wave budget, starting resources and village life.
- **FR-014**: Before each wave the game MUST show which enemy kinds and how many are coming.

**Village, resources, magic**

- **FR-015**: Resources MUST be gold, stone and mana. Gold comes from kills, wave bonuses, market
  and interest; stone from the quarry and a small wave bonus; mana from the church over time.
- **FR-016**: The village MUST offer at least eight building lines, each with three to five
  levels, each level with a cost, requirements (other buildings' levels) and
  lasting bonuses: church, smithy, market, quarry, houses, town wall, masons' lodge, library.
- **FR-017**: Village upgrades MUST be bought only in the build phase; the bonuses of all bought
  levels add up and apply immediately.
- **FR-018**: The church MUST have five stages named and drawn distinctly, ending in a gothic
  cathedral. It MUST heal the village after each wave, generate mana, raise maximum mana, unlock
  spells, and from stage 4 ring bells that stun all non-boss enemies at an interval.
- **FR-019**: For any locked village upgrade the game MUST show the missing requirements and the
  complete ordered list of village upgrades needed to reach it. Requirements are always levels of
  other village buildings (population is expressed through the level of the houses).
- **FR-020**: There MUST be at least five spells: area fire damage with burn, area slow, single
  heavy magic strike, village heal, global stun. Each MUST have a mana cost, a cooldown, an
  unlocking church stage, and three levels (level 1 on unlocking, two upgrades bought in the library).
- **FR-021**: The player MUST be able to save in the build phase and load a saved match; invalid
  files MUST be refused with a reason and without changing the running match.

**Learning**

- **FR-022**: The workshop MUST offer at least 24 missions in at least five tracks: the grid;
  towers; the horde; village and magic; the workshop craft. Tracks can be started in any order.
  Where a mission builds on missions of another track (the spell book on effects and chain
  lightning, the bot on routing and towers), the mission registry names these prerequisites, the
  mission board and the test runner say so, and the game labels the capability as waiting for them. The topics MUST include nested lists, tuples as coordinates, sets, queues and
  breadth-first search, functions as values and sorting keys, composition, class hierarchies with
  overriding, exceptions, recursion, dictionary processing, refactoring, writing tests, debugging
  from tracebacks, JSON data, and simple statistics.
- **FR-023**: Every capability the game takes from the workshop MUST have a stand-in that is used
  while the mission is unsolved, is deliberately and visibly weaker, and is labelled on screen
  with the mission number and title. A stand-in MUST NOT implement the mission's real behaviour.
- **FR-024**: The game MUST run a complete match with an untouched workshop and with any single
  capability solved or unsolved in any combination.
- **FR-025**: An ordinary error raised inside workshop code during play MUST pause the match and
  show file, line, error type, message and mission, and MUST also print the traceback.
- **FR-026**: One key MUST reload the workshop code and start a new match with the same map and
  difficulty, without restarting the program. A reload that fails to import MUST show the error
  panel and keep the previous code.
- **FR-027**: The test runner MUST run one mission, one track or all missions against the
  workshop, or against the reference only with the explicit switch; MUST print German feedback
  per test with expectation, actual result and a hint; MUST exit with status 0 only if everything
  selected passed; and without arguments MUST print the mission board and a suggested next mission.
- **FR-028**: The game MUST show the mission board (solved, in progress, open per mission) and the
  active stand-ins on request, using the results of the last test-runner run.
- **FR-029**: The reference MUST live in a separate package with identical module names, public
  names and signatures, and MUST solve every mission.
- **FR-030**: Debug overlays MUST show, on request, the route distance of every cell as computed
  by the active (workshop or stand-in) code, every tower's range, and frame rate with simulation
  time per step.
- **FR-031**: The workshop craft track MUST contain: a bug hunt with at least three prepared
  faults; a clean-up task with behaviour tests that stay green and tidiness checks to satisfy; an
  own-tests task judged by running the learner's tests against one correct and at least four
  faulty subjects; the save format; the laboratory statistics; the bot.
- **FR-032**: A laboratory command MUST play a given number of matches without a window using a
  given bot, map and difficulty, and print a table of results. Autopilot in the game MUST use the
  same bot interface.
- **FR-033**: Each mission MUST have a German document with: story, what is practised, contract,
  examples, done-when, at least two hidden graded hints, the visible change in the game, and a
  thinking question. A start page, a parents' page, an extension guide and a page of open
  challenges MUST exist.

**Presentation and options**

- **FR-034**: All graphics MUST be drawn by the program and all sounds synthesised by it. The
  window MUST be resizable with preserved proportions and offer full screen.
- **FR-035**: The game MUST offer pause, speeds of 1×, 2× and 4×, sound on/off, and remember
  options between starts. It MUST pause when the window loses focus.
- **FR-036**: Hits, kills, weak hits, spells, effects, building, selling, upgrades, wave start,
  boss arrival, bells, victory and defeat MUST each have a visual signal and, with sound on, an
  audible one.
- **FR-037**: The simulation MUST be independent of the frame rate and reproducible: the same
  seed, map, difficulty and actions give the same result with or without a window.
- **FR-038**: A preview command MUST render a set of scripted scenes to image files without a
  window, for documentation and review.

### Key Entities

- **Map (Karte)**: a grid of terrain characters with orc gates, one village gate and village ground.
- **Building (Bauwerk)**: a tower or palisade on one cell; kind, level, master upgrade, targeting
  rule, amount spent.
- **Enemy (Gegner)**: kind, life, speed, position, reward, village damage, resistances, attached
  effects, abilities, flying or walking.
- **Effect (Effekt)**: a timed modifier on one enemy: slow, poison, burn, stun.
- **Ability (Fähigkeit)**: lasting behaviour of an enemy kind: regenerate, heal others, summon.
- **Wave (Welle)**: an ordered list of enemy kinds with spawn timing.
- **Village (Dorf)**: life, resources, population, the level of each building line, summed bonuses.
- **Spell (Zauber)**: name, level, mana cost, cooldown, effect on enemies or village.
- **Match (Spiel)**: map, difficulty, seed, phase, wave number, all of the above, and the event
  list the presentation reads.
- **Mission**: number, track, title, workshop functions, capability it unlocks, tests, document.
- **Capability (Fähigkeit der Werkbank)**: a group of workshop functions the game uses together,
  with its stand-in.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: With an untouched workshop, the game starts and three waves can be played without
  any error panel; verified automatically without a window.
- **SC-002**: For each capability, solving only that capability (together with the prerequisite
  capabilities its missions name) removes exactly those stand-in labels, and a match plays without
  error in every such combination; verified automatically per capability.
- **SC-003**: The reference passes all mission tests. In the untouched workshop, missions 1–20 and
  24–26 report "still open" and no other error; the craft missions 21–23 report their shipped
  state (21: wrong results or ordinary errors; 22: behaviour passes, tidiness fails; 23: the
  checker names surviving faulty variants).
- **SC-004**: With 200 enemies and 50 towers, one simulation step takes on average no more than
  4 ms and drawing one frame no more than 8 ms on the owner's computer, measured without a window.
- **SC-005**: A scripted reference bot wins the campaign on the easy and normal levels on the
  default map; a one-sided bot (arrow towers only, no village, no magic) loses on normal; an empty
  defence loses on every level before wave 5.
- **SC-006**: A campaign match simulated without a window runs at least 20 times faster than
  real time.
- **SC-007**: The same seed and actions produce an identical final state in two runs, and with
  and without drawing.
- **SC-008**: Every one of the five church stages, every tower kind and level, every enemy kind
  and every spell appears in the preview images, and the five church stages are visibly distinct.
- **SC-009**: Every mission document names only commands, files, functions and keys that exist;
  verified automatically.
- **SC-010**: A newcomer following the start page reaches a running game and a first test result
  with three commands after cloning: install, start the game, test mission 1.

## Assumptions

- The learner is the same child as in version 1 and has the skills listed under Background.
  Version 2 therefore starts above version 1's level and does not re-teach its topics.
- German remains the language of everything the learner reads; identifiers stay German.
- One additional package to install is acceptable; a second is not.
- The game is for one player on a desktop computer with mouse and keyboard, at a base resolution
  of 1280 by 720 that scales with the window.
- Buildings have no life points; only breakers remove them, after a fixed time at the building.
- Projectiles are presentation only: a shot takes effect at the moment it is fired.
- Shortest routes count cells; swamp slows movement but does not change routing. Routing by
  travel time is an open challenge for the learner, not part of this feature.
- Publishing releases, and anything beyond the repository's own automatic checks, is out of scope.
