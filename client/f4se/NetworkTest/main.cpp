#include "../f4mp/Librg.h"

#include <iostream>

using Event = f4mp::networking::Event;

class Entity : public f4mp::networking::Entity
{
public:
	void OnCreate(Event& event) override
	{
		std::cout << _interface->id << ": entity created." << std::endl;
	}

	void OnDestroy(Event& event) override
	{
		std::cout << _interface->id << ": entity destroyed." << std::endl;
	}

	void OnServerUpdate(Event& event) override
	{
		std::cout << _interface->id << ": entity updated on server." << std::endl;
	}

	void OnClientUpdate(Event& event) override
	{
		std::cout << _interface->id << ": entity updated on client." << std::endl;
	}

	void OnMessageReceive(Event& event) override
	{
		std::cout << _interface->id << ": message received." << std::endl;
	}
};

int main()
{
	f4mp::networking::Networking* networking = new f4mp::librg::Librg(true);

	networking->instantiate = [](f4mp::networking::Entity::Type entityType)
	{
		return new Entity();
	};

	networking->onConnectionRequest = [](f4mp::networking::Event& event)
	{
		std::cout << "connection requested." << std::endl;
	};

	networking->onConnectionAccept = [](f4mp::networking::Event& event)
	{
		std::cout << "connection accepted." << std::endl;
	};

	networking->onConnectionRefuse = [](f4mp::networking::Event& event)
	{
		std::cout << "connection refused." << std::endl;
	};

	networking->Start("localhost", 7779);

	while (true)
	{
		networking->Tick();
		zpl_sleep_ms(500);
	}

	return 0;
}