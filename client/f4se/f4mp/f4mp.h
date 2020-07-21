#pragma once

#include "Networking.h"

#include "f4se/PluginAPI.h"

#include <functional>
#include <thread>
#include <atomic>

namespace f4mp
{
	using Event = networking::Event;

	using FormID = UInt32;

	class Entity;

	class F4MP
	{
		friend class Entity;
		friend class InputHandler;

	public:
		static const std::string version;

		F4MP(const F4SEInterface* f4se);
		virtual ~F4MP();

		void Tick();

	private:
		networking::Networking* networking;

		PluginHandle pluginHandle;

		std::thread* tickThread;
		std::atomic_flag tickLock;
		bool ticking;

		void DoNetworking(const std::function<void (networking::Networking* networking)>& callback);

		Entity* Instantiate(networking::Entity::Type entityType);
		void OnConnectionRequest(Event& event);
		void OnConnectionAccept(Event& event);
		void OnConnectionRefuse(Event& event);
	};
}