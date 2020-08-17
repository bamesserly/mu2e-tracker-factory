#include "byhandmeasurement.h"
#include "ui_byhandmeasurement.h"

byHandMeasurement::byHandMeasurement(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::byHandMeasurement)
{
    ui->setupUi(this);
}

byHandMeasurement::~byHandMeasurement()
{
    delete ui;
}
