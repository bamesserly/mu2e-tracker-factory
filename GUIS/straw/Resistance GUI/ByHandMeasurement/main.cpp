#include "byhandmeasurement.h"
#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    byHandMeasurement w;
    w.show();

    return a.exec();
}
