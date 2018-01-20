#include <nc/config.h>
#include <nc/common/Types.h>
#include <nc/common/Foreach.h>
#include <nc/core/Context.h>
#include <nc/core/Driver.h>
#include <nc/core/likec/Tree.h>
#include <nc/core/likec/Declaration.h>
#include <nc/core/image/Image.h>
#include <nc/core/image/Section.h>
#include <nc/core/ir/Program.h>

#include <stdio.h>

#define MAX_OUTPUT      2*1024*1024

char output[MAX_OUTPUT] = { '\0' };

extern "C" const char*
snowman_decompile_by_func(char *filename, char *function)
{
    try
    {
        nc::core::Context context;
        nc::core::Driver::parse(context, filename);
        nc::core::Driver::disassemble(context);
        nc::core::Driver::decompile(context);
        nc::core::likec::CompilationUnit *root = context.tree()->root();

        for ( auto &declaration: root->declarations()) {
            if ( !declaration->identifier().compare(function) &&
                 (nc::core::likec::Declaration::FUNCTION_DEFINITION == declaration->declarationKind())) {
                QString out;
                QTextStream qout(&out, QIODevice::ReadWrite);
                declaration->print(qout);
                qout.flush();
                snprintf(output, sizeof(output), "%s", qout.readAll().toStdString().c_str());
            }
        }
    }
    catch (...)
    {
        /* nothing to do */
    }

    return output;
}

extern "C" const char*
snowman_decompile_by_addr(char *filename, nc::ByteAddr start, nc::ByteAddr end)
{
    try
    {
        nc::core::Context context;
        nc::core::Driver::parse(context, filename);

        /* disassemble the desired function */
        foreach (auto section, context.image()->sections())
        {
            if ((section->isCode() && section->containsAddress(start) && section->containsAddress(end)))
            {
                nc::core::Driver::disassemble(context, section, start, end);
            }
        }

        nc::core::Driver::decompile(context);

        QString out;
        QTextStream qout(&out, QIODevice::ReadWrite);
        context.tree()->print(qout);
        qout.flush();
        snprintf(output, sizeof(output), "%s", qout.readAll().toStdString().c_str());
    }
    catch (...)
    {
        /* nothing to do */
    }

    return output;
}

/* vim:set et sts=4 sw=4: */
