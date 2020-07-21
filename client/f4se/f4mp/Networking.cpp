#include "Networking.h"

#include <algorithm>
#include <stdexcept>

f4mp::networking::MessageOptions::MessageOptions(bool reliable, Entity* target, Entity* except) : reliable(reliable), target(target), except(except)
{
}

void f4mp::networking::Entity::SendMessage(Event::Type messageType, const EventCallback& callback, const MessageOptions& options)
{
	_interface->SendMessage(messageType, callback, options);
}

f4mp::networking::Entity::~Entity()
{
	if (_interface != nullptr)
	{
		delete _interface;
		_interface = nullptr;
	}
}

void f4mp::networking::Networking::Start(const std::string& address, int32_t port)
{
	if (!instantiate)
	{
		throw std::runtime_error("empty instantiate");
	}

	if (!onConnectionRequest)
	{
		throw std::runtime_error("empty onConnectionRequest");
	}

	if (!onConnectionAccept)
	{
		throw std::runtime_error("empty onConnectionAccept");
	}

	if (!onConnectionRefuse)
	{
		throw std::runtime_error("empty onConnectionRefuse");
	}
}

void f4mp::networking::Networking::Create(Entity* entity)
{
	if (entity->_interface != nullptr)
	{
		throw std::runtime_error("entity already created.");
	}

	entity->_interface = CreateEntityInterface();

	Entity::InstantiationID instantiationID = 0;

	for (auto& entityInstantiation : entityInstantiationQueue)
	{
		instantiationID = std::max<Entity::InstantiationID>(instantiationID, entityInstantiation.first + 1);
	}

	entityInstantiationQueue[instantiationID] = entity;
}

f4mp::networking::Entity::_Interface* f4mp::networking::Networking::GetEntityInterface(Entity& entity)
{
	return entity._interface;
}

f4mp::networking::Entity* f4mp::networking::Networking::Instantiate(Entity::InstantiationID instantiationID, Entity::ID entityID, Entity::Type entityType)
{
	Entity* entity = nullptr;

	if (instantiationID >= 0)
	{
		auto entityInstantiation = entityInstantiationQueue.find(instantiationID);
		if (entityInstantiation == entityInstantiationQueue.end())
		{
			throw std::runtime_error("invalid instantiation id");
		}

		entity = entityInstantiation->second;
		entityInstantiationQueue.erase(entityInstantiation);
	}
	else
	{
		entity = instantiate(entityType);
		entity->_interface = CreateEntityInterface();
	}

	entity->_interface->id = entityID;

	return entity;
}
