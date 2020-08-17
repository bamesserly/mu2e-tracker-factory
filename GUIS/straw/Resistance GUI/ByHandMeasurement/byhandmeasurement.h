#ifndef BYHANDMEASUREMENT_H
#define BYHANDMEASUREMENT_H

#include <QWidget>

namespace Ui {
class byHandMeasurement;
}

class byHandMeasurement : public QWidget
{
    Q_OBJECT

public:
    explicit byHandMeasurement(QWidget *parent = 0);
    ~byHandMeasurement();

private:
    Ui::byHandMeasurement *ui;
};

#endif // BYHANDMEASUREMENT_H
