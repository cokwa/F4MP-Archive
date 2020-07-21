#include "F4MP.h"
#include "Librg.h"
#include "Entity.h"
#include "Player.h"

#include "f4se/PluginManager.h"
#include "f4se/GameInput.h"
#include "f4se/GameMenus.h"
#include "f4se/PapyrusDelayFunctors.h"

const std::string f4mp::F4MP::version = "0.1indev";

namespace f4mp
{
	class InputHandler : public PlayerInputHandler
	{
		friend F4MP;

	public:
		InputHandler(F4MP& instance) : PlayerInputHandler(), instance(instance) { }

		~InputHandler()
		{
			PlayerControls* controls = *g_playerControls;
			if (controls == nullptr)
			{
				return;
			}

			PlayerInputHandler* _this = this;
			SInt64 index = controls->inputEvents1.GetItemIndex(_this);
			if (index < 0)
			{
				return;
			}

			controls->inputEvents1.Remove(index);
		}

		void OnButtonEvent(ButtonEvent* inputEvent)
		{
			if ((*g_ui)->numPauseGame)
			{
				return;
			}

			if (inputEvent->deviceType != InputEvent::kDeviceType_Keyboard)
			{
				return;
			}

			if (inputEvent->isDown != 1.f || inputEvent->timer != 0.f)
			{
				return;
			}

			switch (inputEvent->keyMask)
			{
			case 112:
				instance.DoNetworking([=](networking::Networking* networking)
					{
						networking->Start("localhost", 7779);
					});
				break;
			}
		}

	private:
		F4MP& instance;
	};
}

std::unique_ptr<f4mp::InputHandler> inputHandler;

f4mp::F4MP::F4MP(const F4SEInterface* f4se) : networking(nullptr), pluginHandle(kPluginHandle_Invalid), tickThread(nullptr), ticking(true)
{
	networking = new librg::Librg(false);

	networking->instantiate = [=](networking::Entity::Type entityType) { return Instantiate(entityType); };
	networking->onConnectionRequest = [=](Event& event) { OnConnectionRequest(event); };
	networking->onConnectionAccept = [=](Event& event) { OnConnectionAccept(event); };
	networking->onConnectionRefuse = [=](Event& event) { OnConnectionRefuse(event); };

	inputHandler = std::make_unique<InputHandler>(*this);

	pluginHandle = f4se->GetPluginHandle();

	// bad code?
	static F4MP* instance;
	instance = this;

	((F4SEMessagingInterface*)f4se->QueryInterface(kInterface_Messaging))->RegisterListener(pluginHandle, "F4SE", [](F4SEMessagingInterface::Message* msg)
		{
			switch (msg->type)
			{
			case F4SEMessagingInterface::kMessage_GameLoaded:
				instance->ticking = true;
				instance->tickThread = new std::thread(&F4MP::Tick, instance);
				(*g_playerControls)->inputEvents1.Push(inputHandler.get());
				break;
			}
		});
}

void f4mp::F4MP::Tick()
{
	while (ticking)
	{
		DoNetworking([=](networking::Networking* networking)
			{
				networking->Tick();
			});

		Sleep(1);
	}
}

void f4mp::F4MP::DoNetworking(const std::function<void(networking::Networking* networking)>& callback)
{
	while (tickLock.test_and_set(std::memory_order_acquire));

	callback(networking);

	tickLock.clear(std::memory_order_release);
}

f4mp::Entity* f4mp::F4MP::Instantiate(networking::Entity::Type entityType)
{
	return new Entity({ 0, 0, 0 });
}

void f4mp::F4MP::OnConnectionRequest(Event& event)
{
	printf("connection requested\n");
}

void f4mp::F4MP::OnConnectionAccept(Event& event)
{
	printf("connection accepted\n");
}

void f4mp::F4MP::OnConnectionRefuse(Event& event)
{
	printf("connection refused\n");
}

f4mp::F4MP::~F4MP()
{
	if (tickThread != nullptr)
	{
		ticking = false;
		tickThread->join();

		delete tickThread;
		tickThread = nullptr;
	}

	if (networking != nullptr)
	{
		delete networking;
		networking = nullptr;
	}
}