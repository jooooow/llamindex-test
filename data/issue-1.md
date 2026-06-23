@zupdaz
zupdaz
opened on May 11, 2025
Hello,
I am using the create-llama ts and I would like to customize the Chat UI Interface, specifically to remove the "Star on GitHub" button and potentially apply some global CSS overrides.

I am not a fan of modification of node modules so in previous versions setting up globals.css in src/app worked for me. On 0.5.13 I cannot seem to be able to override the setting and don't know what is causing this behaviour.

I would appreciate guidance on the best way to achieve this. Is there a recommended approach for injecting global styles? If this is documented somewhere, please point me to the right resources. Apologies, since this is not a real issue but more mine incompetency.

With 0.5.13 I get "llamaindex was already imported. This breaks constructor checks and will lead to issues!" after running dev. Maybe this is the root of the issue but not sure. npm ls llamaindex returns:
├─┬ @llamaindex/server@0.2.0
│ └── llamaindex@0.10.5 deduped
└── llamaindex@0.10.5

Activity
marcusschiesser commented on May 12, 2025
@marcusschiesser
marcusschiesser
on May 12, 2025
Contributor
@zupdaz I see three ways to do this:

we add more uiConfigs to https://www.npmjs.com/package/@llamaindex/server - which ones would you like?
you extend https://www.npmjs.com/package/@llamaindex/server with your own code
you create a nextjs app and inline the code from https://github.com/run-llama/create-llama/tree/main/packages/server/src
lczarne commented on May 13, 2025
@lczarne
lczarne
on May 13, 2025
@marcusschiesser Is there a way to customize create-llama app this way? For example I create Rag Agent app. Everything is great but I would like to provide some changes in the UI. Can you provide some examples?

zupdaz commented on May 13, 2025
@zupdaz
zupdaz
on May 13, 2025
Author
@marcusschiesser
To really make upgrades hassle free I would love to be able to modify at least the header of llama - links, logo, github button located in node_modules@llamaindex\server\server\app\components\ui\chat\chat-header.tsx within src or components.


marcusschiesser
changed the title [-]CSS overrides - how to achive with create-llama[/-] [+]Customize Header for LlamaIndexServer[/+] on May 13, 2025
marcusschiesser commented on May 13, 2025
@marcusschiesser
marcusschiesser
on May 13, 2025
Contributor
@lczarne what do you want to customize?

marcusschiesser commented on May 13, 2025
@marcusschiesser
marcusschiesser
on May 13, 2025
Contributor
@zupdaz customizing the header should not a big problem. changes:

copy https://github.com/run-llama/create-llama/blob/main/packages/server/next/app/components/ui/chat/chat-header.tsx into the components dir
use this dynamic component in the chat section
update README that header can be modified

marcusschiesser
assigned 
thucpn
on May 13, 2025

marcusschiesser
moved this to Todo in  Frameworkon May 13, 2025

marcusschiesser
added this to  Frameworkon May 13, 2025
marcusschiesser commented on May 14, 2025
@marcusschiesser
marcusschiesser
on May 14, 2025
Contributor
Better: we add a new header UI config that points to the header.tsx file (which is in the components dir)

lczarne commented on May 14, 2025
@lczarne
lczarne
on May 14, 2025
@marcusschiesser Would be great to Customize the whole chat ui. Would be great for spinning different apps with create-llama and then changing the UI to your own needs/preferences. Somehow I cannot do it with those generated components - or maybe I just don't know the way. Having the direct access to UI code in app created by create-llama would be great.

marcusschiesser commented on May 15, 2025
@marcusschiesser
marcusschiesser
on May 15, 2025
Contributor
@lczarne to allow the UI to be fully customizable we would need to generate a NextJS project which is out of the scope for the LlamaIndexServer - we can discuss how to do that in #620


marcusschiesser
mentioned this on May 15, 2025
Generate fully customizable NextJS code #620

marcusschiesser
moved this from Todo to In Progress in  Frameworkon May 23, 2025
marcusschiesser commented on May 27, 2025
@marcusschiesser
marcusschiesser
on May 27, 2025
Contributor
closing this as llamaindex server allows to add layout files: https://www.npmjs.com/package/@llamaindex/server#custom-layout


marcusschiesser
closed this as completedon May 27, 2025

github-project-automation
moved this from In Progress to Done in  Frameworkon May 27, 2025
